from django.urls import path

from .views import (
    LLMModelCreateView,
    LLMModelDeleteView,
    LLMModelListView,
    LLMModelUpdateView,
    PromptTemplateCreateView,
    PromptTemplateDeleteView,
    PromptTemplateListView,
    PromptTemplateUpdateView,
)

app_name = "llm"

urlpatterns = [
    path("models/", LLMModelListView.as_view(), name="model_list"),
    path("models/create/", LLMModelCreateView.as_view(), name="model_create"),
    path("models/<int:pk>/edit/", LLMModelUpdateView.as_view(), name="model_edit"),
    path("models/<int:pk>/delete/", LLMModelDeleteView.as_view(), name="model_delete"),
    path("prompts/", PromptTemplateListView.as_view(), name="prompt_list"),
    path("prompts/create/", PromptTemplateCreateView.as_view(), name="prompt_create"),
    path("prompts/<int:pk>/edit/", PromptTemplateUpdateView.as_view(), name="prompt_edit"),
    path("prompts/<int:pk>/delete/", PromptTemplateDeleteView.as_view(), name="prompt_delete"),
]

