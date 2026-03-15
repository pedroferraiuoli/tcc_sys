from django.urls import path

from .views import (
    BatchExperimentView,
    ExperimentCreateView,
    ExperimentDeleteView,
    ExperimentListView,
)

app_name = "experiments"

urlpatterns = [
    path("", ExperimentListView.as_view(), name="list"),
    path("create/", ExperimentCreateView.as_view(), name="create"),
    path("batch/", BatchExperimentView.as_view(), name="batch"),
    path("<int:experiment_id>/delete/", ExperimentDeleteView.as_view(), name="delete"),
]

