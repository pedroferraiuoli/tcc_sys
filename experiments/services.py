from __future__ import annotations

import logging
from datetime import datetime
from typing import Iterable, List

from django.db import transaction
from django.utils import timezone

from documents.models import Document
from evaluation.services import evaluate_experiment
from llm.models import LLMModel, PromptTemplate
from llm.services import get_default_prompt
from pipelines.models import PipelineDefinition
from pipelines.services import PipelineResult, run_pipeline
from .models import Experiment, ExperimentResult, ExperimentStatus

logger = logging.getLogger(__name__)


@transaction.atomic
def run_experiment(experiment: Experiment) -> Experiment:
    """
    Executa um experimento individual (sincronamente).

    Esta função encapsula o fluxo:
    pipeline → LLM → armazenamento de resultado → avaliação automática.
    """
    logger.info("Iniciando experimento %s", experiment.pk)
    experiment.status = ExperimentStatus.RUNNING
    experiment.started_at = timezone.now()
    experiment.error_message = ""
    experiment.save(update_fields=["status", "started_at", "error_message"])

    try:
        pipeline_result: PipelineResult = run_pipeline(
            pipeline=experiment.pipeline,
            document=experiment.document,
            llm_model=experiment.llm_model,
            prompt=experiment.prompt,
        )

        ExperimentResult.objects.update_or_create(
            experiment=experiment,
            defaults={
                "generated_tags": pipeline_result.tags_text,
                "runtime_seconds": pipeline_result.runtime_seconds,
                "num_tokens": pipeline_result.num_tokens_estimated,
            },
        )

        # Avaliação automática
        evaluate_experiment(experiment)

        experiment.status = ExperimentStatus.DONE
        experiment.finished_at = timezone.now()
        experiment.save(update_fields=["status", "finished_at"])
        logger.info("Experimento %s concluído com sucesso", experiment.pk)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Falha ao executar experimento %s", experiment.pk)
        experiment.status = ExperimentStatus.FAILED
        experiment.finished_at = timezone.now()
        experiment.error_message = str(exc)
        experiment.save(update_fields=["status", "finished_at", "error_message"])
        raise

    return experiment


def create_experiment(
    *,
    document: Document,
    llm_model: LLMModel,
    pipeline: PipelineDefinition,
    prompt: PromptTemplate | None = None,
) -> Experiment:
    """Cria um experimento usando o prompt padrão, se nenhum for fornecido."""
    if prompt is None:
        prompt = get_default_prompt()
        if prompt is None:
            raise ValueError(
                "Nenhum prompt padrão definido. Cadastre um PromptTemplate com is_default=True."
            )

    experiment = Experiment.objects.create(
        document=document,
        llm_model=llm_model,
        pipeline=pipeline,
        prompt=prompt,
    )
    return experiment


def run_experiment_now(
    *,
    document: Document,
    llm_model: LLMModel,
    pipeline: PipelineDefinition,
    prompt: PromptTemplate | None = None,
) -> Experiment:
    """Helper que cria e já executa um experimento."""
    experiment = create_experiment(
        document=document,
        llm_model=llm_model,
        pipeline=pipeline,
        prompt=prompt,
    )
    return run_experiment(experiment)


def run_batch_experiments(
    *,
    documents: Iterable[Document],
    llm_models: Iterable[LLMModel],
    pipelines: Iterable[PipelineDefinition],
    prompt: PromptTemplate | None = None,
) -> List[Experiment]:
    """
    Executa experimentos em lote para todas as combinações fornecidas.

    Pode ser adaptado futuramente para uso com Celery (tarefas assíncronas).
    """
    if prompt is None:
        prompt = get_default_prompt()
        if prompt is None:
            raise ValueError(
                "Nenhum prompt padrão definido. Cadastre um PromptTemplate com is_default=True."
            )

    experiments: list[Experiment] = []
    for document in documents:
        for llm_model in llm_models:
            for pipeline in pipelines:
                exp = create_experiment(
                    document=document,
                    llm_model=llm_model,
                    pipeline=pipeline,
                    prompt=prompt,
                )
                run_experiment(exp)
                experiments.append(exp)
    return experiments

