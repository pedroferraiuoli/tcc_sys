from django.urls import path

from .views import DocumentDetailView, DocumentListView, DocumentUploadView

app_name = "documents"

urlpatterns = [
    path("", DocumentListView.as_view(), name="list"),
    path("upload/", DocumentUploadView.as_view(), name="upload"),
    path("<int:pk>/", DocumentDetailView.as_view(), name="detail"),
]

