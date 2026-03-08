from __future__ import annotations

from django import forms

from .models import Document


class DocumentUploadForm(forms.Form):
    pdf_file = forms.FileField(label="Arquivo PDF")


class DocumentTagsForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["human_tags"]
        widgets = {
            "human_tags": forms.Textarea(
                attrs={"rows": 3, "placeholder": "tag1, tag2, tag3"}
            )
        }

