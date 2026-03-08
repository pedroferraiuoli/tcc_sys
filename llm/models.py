from __future__ import annotations

from django.db import models


class LLMModel(models.Model):
    """Configuração de um modelo de linguagem disponível no sistema."""

    class Provider(models.TextChoices):
        OLLAMA = "ollama", "Ollama"
        OPENAI = "openai", "OpenAI"
        OTHER = "other", "Outro"

    name = models.CharField("nome do modelo", max_length=100)
    provider = models.CharField(
        "provider",
        max_length=20,
        choices=Provider.choices,
        default=Provider.OLLAMA,
    )
    endpoint = models.URLField(
        "endpoint",
        blank=True,
        help_text="Ex.: http://localhost:11434 para Ollama.",
    )
    model_size = models.CharField("tamanho do modelo", max_length=50, blank=True)
    description = models.TextField("descrição", blank=True)
    is_active = models.BooleanField("ativo", default=True)

    class Meta:
        verbose_name = "Modelo LLM"
        verbose_name_plural = "Modelos LLM"

    def __str__(self) -> str:
        return self.name


class PromptTemplate(models.Model):
    """
    Prompt armazenado para garantir reprodutibilidade científica.

    Exemplo de conteúdo recomendado:
    \"Leia o seguinte texto e gere uma lista de palavras‑chave que representem
    os principais temas do documento. Retorne apenas uma lista de keywords
    separadas por vírgula.\"
    """

    name = models.CharField("nome", max_length=100, unique=True)
    text = models.TextField("texto do prompt")
    is_default = models.BooleanField(
        "é prompt padrão", default=False, help_text="Usado como prompt padrão nos experimentos."
    )
    created_at = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        verbose_name = "Prompt"
        verbose_name_plural = "Prompts"

    def __str__(self) -> str:
        return self.name

