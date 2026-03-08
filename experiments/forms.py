from __future__ import annotations

from django import forms

from documents.models import Document
from llm.models import LLMModel, PromptTemplate
from pipelines.models import PipelineDefinition


class ExperimentCreateForm(forms.Form):
    document = forms.ModelChoiceField(
        queryset=Document.objects.all(), label="Documento"
    )
    llm_model = forms.ModelChoiceField(
        queryset=LLMModel.objects.filter(is_active=True), label="Modelo LLM"
    )
    pipeline = forms.ModelChoiceField(
        queryset=PipelineDefinition.objects.all(), label="Pipeline"
    )
    prompt = forms.ModelChoiceField(
        queryset=PromptTemplate.objects.all(),
        label="Prompt",
        required=False,
        help_text="Se vazio, será utilizado o prompt padrão configurado.",
    )


class BatchExperimentForm(forms.Form):
    documents = forms.ModelMultipleChoiceField(
        queryset=Document.objects.all(),
        label="Documentos",
        required=True,
    )
    llm_models = forms.ModelMultipleChoiceField(
        queryset=LLMModel.objects.filter(is_active=True),
        label="Modelos LLM",
        required=True,
    )
    pipelines = forms.ModelMultipleChoiceField(
        queryset=PipelineDefinition.objects.all(),
        label="Pipelines",
        required=True,
    )
    prompt = forms.ModelChoiceField(
        queryset=PromptTemplate.objects.all(),
        label="Prompt",
        required=False,
    )

