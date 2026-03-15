from __future__ import annotations

import logging
import secrets
import threading
from datetime import datetime
from typing import Iterable, List

from django.db import close_old_connections
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
    batch_code: str = "",
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
        batch_code=batch_code,
    )
    return experiment


def run_experiment_now(
    *,
    document: Document,
    llm_model: LLMModel,
    pipeline: PipelineDefinition,
    prompt: PromptTemplate | None = None,
    batch_code: str = "",
) -> Experiment:
    """Helper que cria e já executa um experimento."""
    experiment = create_experiment(
        document=document,
        llm_model=llm_model,
        pipeline=pipeline,
        prompt=prompt,
        batch_code=batch_code,
    )
    return run_experiment(experiment)


def generate_batch_code() -> str:
    """Gera um código curto para agrupar experimentos criados por batch."""
    return secrets.token_hex(6).upper()


def _run_batch_worker(
    *,
    document_ids: list[int],
    llm_model_ids: list[int],
    pipeline_ids: list[int],
    prompt_id: int | None,
    batch_code: str,
) -> None:
    # Isola conexões na thread de background para evitar reuse incorreto.
    close_old_connections()
    try:
        documents = Document.objects.filter(id__in=document_ids).order_by("id")
        llm_models = LLMModel.objects.filter(id__in=llm_model_ids).order_by("id")
        pipelines = PipelineDefinition.objects.filter(id__in=pipeline_ids).order_by("id")
        prompt = PromptTemplate.objects.filter(id=prompt_id).first() if prompt_id else None

        logger.info("Iniciando worker do batch %s", batch_code)
        for document in documents:
            for llm_model in llm_models:
                for pipeline in pipelines:
                    exp = create_experiment(
                        document=document,
                        llm_model=llm_model,
                        pipeline=pipeline,
                        prompt=prompt,
                        batch_code=batch_code,
                    )
                    try:
                        run_experiment(exp)
                    except Exception:  # noqa: BLE001
                        # O erro já é persistido em run_experiment; seguimos com o lote.
                        continue
        logger.info("Batch %s finalizado", batch_code)
    finally:
        close_old_connections()


def run_batch_experiments_async(
    *,
    documents: Iterable[Document],
    llm_models: Iterable[LLMModel],
    pipelines: Iterable[PipelineDefinition],
    prompt: PromptTemplate | None = None,
) -> tuple[str, int]:
    """
    Dispara execução em lote em thread de background e retorna imediatamente.

    Retorna (batch_code, total_esperado_de_experimentos).
    """
    document_ids = [doc.id for doc in documents]
    llm_model_ids = [model.id for model in llm_models]
    pipeline_ids = [pipeline.id for pipeline in pipelines]
    prompt_id = prompt.id if prompt else None

    total = len(document_ids) * len(llm_model_ids) * len(pipeline_ids)
    batch_code = generate_batch_code()

    worker = threading.Thread(
        target=_run_batch_worker,
        kwargs={
            "document_ids": document_ids,
            "llm_model_ids": llm_model_ids,
            "pipeline_ids": pipeline_ids,
            "prompt_id": prompt_id,
            "batch_code": batch_code,
        },
        daemon=True,
        name=f"batch-experiments-{batch_code}",
    )
    worker.start()

    logger.info("Batch %s disparado em background (total=%s)", batch_code, total)
    return batch_code, total


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

