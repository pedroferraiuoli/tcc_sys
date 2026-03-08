from django.contrib import admin

from .models import EvaluationResult


@admin.register(EvaluationResult)
class EvaluationResultAdmin(admin.ModelAdmin):
    list_display = (
        "experiment",
        "document",
        "precision",
        "recall",
        "f1_score",
        "accuracy",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = ("document__file_name",)

