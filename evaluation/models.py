from __future__ import annotations

from django.db import models

from documents.models import Document
from experiments.models import Experiment


class EvaluationResult(models.Model):
    """Métricas calculadas para um experimento em relação às tags humanas."""

    experiment = models.OneToOneField(
        Experiment,
        on_delete=models.CASCADE,
        related_name="evaluation",
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="evaluations",
    )

    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    accuracy = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Resultado de Avaliação"
        verbose_name_plural = "Resultados de Avaliação"

    def __str__(self) -> str:
        return f"Avaliação exp {self.experiment_id}"

