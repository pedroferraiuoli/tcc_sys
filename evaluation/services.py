from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

from django.db import transaction

from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from documents.models import Document
from experiments.models import Experiment, ExperimentResult
from .models import EvaluationResult


def _normalize_tag(tag: str) -> str:
    return tag.strip().lower()


def parse_tags(text: str) -> List[str]:
    """Converte uma string de tags separadas por vírgula em lista normalizada."""
    if not text:
        return []
    parts = [p.strip() for p in text.split(",")]
    return [_normalize_tag(p) for p in parts if p]


@dataclass
class Metrics:
    precision: float
    recall: float
    f1: float
    accuracy: float | None


def compute_metrics(human_tags: Iterable[str], predicted_tags: Iterable[str]) -> Metrics:
    """Calcula métricas de classificação multi‑label a partir de conjuntos de tags."""
    human_set = {t for t in (_normalize_tag(t) for t in human_tags) if t}
    pred_set = {t for t in (_normalize_tag(t) for t in predicted_tags) if t}

    all_labels = sorted(human_set | pred_set)
    if not all_labels:
        return Metrics(precision=0.0, recall=0.0, f1=0.0, accuracy=None)

    y_true = [1 if label in human_set else 0 for label in all_labels]
    y_pred = [1 if label in pred_set else 0 for label in all_labels]

    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    accuracy = accuracy_score(y_true, y_pred)

    return Metrics(
        precision=float(precision),
        recall=float(recall),
        f1=float(f1),
        accuracy=float(accuracy),
    )


@transaction.atomic
def evaluate_experiment(experiment: Experiment) -> EvaluationResult:
    """
    Calcula métricas para um experimento com base nas tags humanas do documento.
    """
    if not hasattr(experiment, "result"):
        raise ValueError("Experimento ainda não possui resultado para avaliar.")

    result: ExperimentResult = experiment.result
    document: Document = experiment.document

    human_tags = document.get_human_tags_list()
    predicted_tags = parse_tags(result.generated_tags)

    metrics = compute_metrics(human_tags, predicted_tags)

    evaluation, _ = EvaluationResult.objects.update_or_create(
        experiment=experiment,
        defaults={
            "document": document,
            "precision": metrics.precision,
            "recall": metrics.recall,
            "f1_score": metrics.f1,
            "accuracy": metrics.accuracy,
        },
    )
    return evaluation

