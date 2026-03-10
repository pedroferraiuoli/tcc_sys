from __future__ import annotations

from django import forms

from .models import LLMModel, PromptTemplate


class LLMModelForm(forms.ModelForm):
    class Meta:
        model = LLMModel
        fields = [
            "name",
            "provider",
            "endpoint",
            "model_size",
            "description",
            "is_active",
        ]


class PromptTemplateForm(forms.ModelForm):
    class Meta:
        model = PromptTemplate
        fields = [
            "name",
            "text",
            "is_default",
        ]

