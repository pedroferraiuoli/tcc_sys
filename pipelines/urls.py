from django.urls import path

from .views import (
    PipelineCreateView,
    PipelineDeleteView,
    PipelineListView,
    PipelineUpdateView,
)

app_name = "pipelines"

urlpatterns = [
    path("", PipelineListView.as_view(), name="list"),
    path("create/", PipelineCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", PipelineUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", PipelineDeleteView.as_view(), name="delete"),
]

