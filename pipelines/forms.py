from __future__ import annotations

from django import forms

from .models import PipelineDefinition


class PipelineDefinitionForm(forms.ModelForm):
    class Meta:
        model = PipelineDefinition
        fields = [
            "name",
            "type",
            "description",
            "chunk_size",
            "top_k",
        ]

