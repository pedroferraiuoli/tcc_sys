from __future__ import annotations

from django.db import models


class PipelineType(models.TextChoices):
    DIRECT = "direct", "Extração direta"
    RAG = "rag", "RAG (Retrieval-Augmented Generation)"


class PipelineDefinition(models.Model):
    """Define um pipeline de processamento documental."""

    name = models.CharField("nome", max_length=100, unique=True)
    type = models.CharField(
        "tipo de pipeline", max_length=20, choices=PipelineType.choices
    )
    description = models.TextField("descrição", blank=True)

    # Parâmetros relevantes apenas para RAG
    chunk_size = models.PositiveIntegerField(
        "tamanho do chunk",
        default=600,
        help_text="Tamanho aproximado do chunk em tokens (recomendado entre 500 e 800).",
    )
    top_k = models.PositiveIntegerField(
        "top-k",
        default=3,
        help_text="Número de chunks mais relevantes recuperados (3 ou 5).",
    )

    created_at = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        verbose_name = "Pipeline"
        verbose_name_plural = "Pipelines"

    def __str__(self) -> str:
        return self.name

    @property
    def is_rag(self) -> bool:
        return self.type == PipelineType.RAG

    @property
    def is_direct(self) -> bool:
        return self.type == PipelineType.DIRECT

