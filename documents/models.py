from __future__ import annotations

from django.db import models


class Document(models.Model):
    """Representa um documento PDF carregado no sistema."""

    file_name = models.CharField("nome do arquivo", max_length=255)
    pdf_file = models.FileField("arquivo PDF", upload_to="documents/")
    extracted_text = models.TextField("texto extraído", blank=True)
    upload_date = models.DateTimeField("data de upload", auto_now_add=True)
    num_pages = models.PositiveIntegerField("número de páginas", default=0)

    # Lista de palavras‑chave definidas manualmente (ground truth),
    # separadas por vírgula.
    human_tags = models.TextField(
        "tags humanas (ground truth)",
        blank=True,
        help_text="Lista de palavras‑chave separadas por vírgula.",
    )

    class Meta:
        ordering = ["-upload_date"]
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"

    def __str__(self) -> str:
        return self.file_name

    def get_human_tags_list(self) -> list[str]:
        """Retorna as tags humanas como lista normalizada."""
        if not self.human_tags:
            return []
        tags = [t.strip() for t in self.human_tags.split(",")]
        return [t for t in tags if t]

    def set_human_tags_list(self, tags: list[str]) -> None:
        """Atualiza o campo de tags humanas a partir de uma lista."""
        normalized = [t.strip() for t in tags if t and t.strip()]
        self.human_tags = ", ".join(normalized)

