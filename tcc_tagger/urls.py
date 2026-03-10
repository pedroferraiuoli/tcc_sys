from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView


urlpatterns = [
    path("", RedirectView.as_view(pattern_name="documents:list", permanent=False)),
    path("admin/", admin.site.urls),
    path("documents/", include("documents.urls", namespace="documents")),
    path("experiments/", include("experiments.urls", namespace="experiments")),
    path("evaluation/", include("evaluation.urls", namespace="evaluation")),
    path("llm/", include("llm.urls", namespace="llm")),
    path("pipelines/", include("pipelines.urls", namespace="pipelines")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
