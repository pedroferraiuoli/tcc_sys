from __future__ import annotations

from django.core.management.base import BaseCommand

from llm.models import PromptTemplate
from pipelines.models import PipelineDefinition, PipelineType


PROMPT_NAME = "Padrão"
PROMPT_TEXT = """Read the following text and generate a list of keywords that represent the main topics of the document.
Return only the keywords, separated by commas.
Do not include explanations, numbering, bullet points, or any additional text.
The output must contain only the keywords separated by commas on a single line."""

PIPELINE_NAME = "Baseline direta"


class Command(BaseCommand):
    help = "Cria dados básicos: Prompt padrão e pipeline 'Baseline direta'."

    def handle(self, *args, **options):
        # Prompt padrão
        prompt, created_prompt = PromptTemplate.objects.get_or_create(
            name=PROMPT_NAME,
            defaults={
                "text": PROMPT_TEXT,
                "is_default": True,
            },
        )

        # Se já existir outro prompt default, mantemos apenas este como padrão
        # if not created_prompt and not prompt.is_default:
        #     prompt.is_default = True
        #     prompt.text = PROMPT_TEXT
        #     prompt.save(update_fields=["is_default", "text"])

        PromptTemplate.objects.exclude(pk=prompt.pk).filter(is_default=True).update(
            is_default=False
        )

        # Pipeline "Baseline direta" (Extração direta)
        pipeline_defaults = {
            "type": PipelineType.DIRECT,
            "description": "Pipeline baseline: extração direta do texto completo do documento.",
            "chunk_size": 600,
            "top_k": 3,
        }
        pipeline, created_pipeline = PipelineDefinition.objects.get_or_create(
            name=PIPELINE_NAME,
            defaults=pipeline_defaults,
        )
        # if not created_pipeline:
        #     for field, value in pipeline_defaults.items():
        #         setattr(pipeline, field, value)
        #     pipeline.save()

        self.stdout.write(self.style.SUCCESS("Prompt padrão e pipeline 'Baseline direta' criados/atualizados com sucesso."))
