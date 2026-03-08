from django.contrib import admin

from .models import LLMModel, PromptTemplate


@admin.register(LLMModel)
class LLMModelAdmin(admin.ModelAdmin):
    list_display = ("name", "provider", "endpoint", "model_size", "is_active")
    list_filter = ("provider", "is_active")
    search_fields = ("name", "description")


@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "is_default", "created_at")
    list_filter = ("is_default", "created_at")
    search_fields = ("name", "text")

