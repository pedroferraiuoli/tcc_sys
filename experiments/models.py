from __future__ import annotations

from django.db import models

from documents.models import Document
from llm.models import LLMModel, PromptTemplate
from pipelines.models import PipelineDefinition


class ExperimentStatus(models.TextChoices):
    PENDING = "pending", "Pendente"
    RUNNING = "running", "Em execução"
    DONE = "done", "Concluído"
    FAILED = "failed", "Falhou"


class Experiment(models.Model):
    """Representa a configuração de um experimento de taggeamento."""

    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="experiments"
    )
    llm_model = models.ForeignKey(
        LLMModel, on_delete=models.CASCADE, related_name="experiments"
    )
    pipeline = models.ForeignKey(
        PipelineDefinition, on_delete=models.CASCADE, related_name="experiments"
    )
    prompt = models.ForeignKey(
        PromptTemplate,
        on_delete=models.PROTECT,
        related_name="experiments",
        help_text="Prompt utilizado para garantir reprodutibilidade.",
    )

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    started_at = models.DateTimeField("iniciado em", null=True, blank=True)
    finished_at = models.DateTimeField("finalizado em", null=True, blank=True)
    status = models.CharField(
        "status",
        max_length=20,
        choices=ExperimentStatus.choices,
        default=ExperimentStatus.PENDING,
    )
    error_message = models.TextField("erro", blank=True)

    class Meta:
        verbose_name = "Experimento"
        verbose_name_plural = "Experimentos"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Exp #{self.pk} - {self.document.file_name} - {self.llm_model.name} - {self.pipeline.name}"


class ExperimentResult(models.Model):
    """Resultado bruto de um experimento."""

    experiment = models.OneToOneField(
        Experiment,
        on_delete=models.CASCADE,
        related_name="result",
    )
    generated_tags = models.TextField(
        "tags geradas",
        help_text="Lista de palavras‑chave geradas pelo modelo, separadas por vírgula.",
    )
    runtime_seconds = models.FloatField("tempo de execução (s)")
    num_tokens = models.PositiveIntegerField(
        "número estimado de tokens", null=True, blank=True
    )
    estimated_cost = models.DecimalField(
        "custo estimado",
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Campo opcional para custo computacional/financeiro.",
    )

    created_at = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        verbose_name = "Resultado de Experimento"
        verbose_name_plural = "Resultados de Experimentos"

    def __str__(self) -> str:
        return f"Resultado do experimento {self.experiment_id}"

