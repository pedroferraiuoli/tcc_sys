from django.contrib import admin

from .models import PipelineDefinition


@admin.register(PipelineDefinition)
class PipelineDefinitionAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "chunk_size", "top_k", "created_at")
    list_filter = ("type", "created_at")
    search_fields = ("name", "description")

