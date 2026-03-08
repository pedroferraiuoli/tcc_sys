from django.contrib import admin

from .models import Experiment, ExperimentResult


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "document",
        "llm_model",
        "pipeline",
        "status",
        "created_at",
        "started_at",
        "finished_at",
    )
    list_filter = ("status", "pipeline", "llm_model", "created_at")
    search_fields = ("document__file_name",)
    readonly_fields = ("created_at", "started_at", "finished_at", "error_message")


@admin.register(ExperimentResult)
class ExperimentResultAdmin(admin.ModelAdmin):
    list_display = (
        "experiment",
        "runtime_seconds",
        "num_tokens",
        "estimated_cost",
        "created_at",
    )
    search_fields = ("experiment__document__file_name", "generated_tags")

