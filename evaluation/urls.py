from django.urls import path

from .views import document_dashboard, export_results_csv, overall_dashboard

app_name = "evaluation"

urlpatterns = [
    path("document/<int:document_id>/", document_dashboard, name="document_dashboard"),
    path("overall/", overall_dashboard, name="overall_dashboard"),
    path("export/csv/", export_results_csv, name="export_csv"),
]

