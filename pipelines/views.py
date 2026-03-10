from __future__ import annotations

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .forms import PipelineDefinitionForm
from .models import PipelineDefinition


class PipelineListView(View):
    def get(self, request):
        pipelines = PipelineDefinition.objects.all().order_by("name")
        return render(
            request,
            "pipelines/pipeline_list.html",
            {"pipelines": pipelines},
        )


class PipelineCreateView(View):
    def get(self, request):
        form = PipelineDefinitionForm()
        return render(request, "pipelines/pipeline_form.html", {"form": form})

    def post(self, request):
        form = PipelineDefinitionForm(request.POST)
        if not form.is_valid():
            return render(request, "pipelines/pipeline_form.html", {"form": form})

        form.save()
        messages.success(request, "Pipeline criado com sucesso.")
        return redirect("pipelines:list")


class PipelineUpdateView(View):
    def get(self, request, pk: int):
        pipeline = get_object_or_404(PipelineDefinition, pk=pk)
        form = PipelineDefinitionForm(instance=pipeline)
        return render(
            request,
            "pipelines/pipeline_form.html",
            {
                "form": form,
                "object": pipeline,
            },
        )

    def post(self, request, pk: int):
        pipeline = get_object_or_404(PipelineDefinition, pk=pk)
        form = PipelineDefinitionForm(request.POST, instance=pipeline)
        if not form.is_valid():
            return render(
                request,
                "pipelines/pipeline_form.html",
                {
                    "form": form,
                    "object": pipeline,
                },
            )

        form.save()
        messages.success(request, "Pipeline atualizado com sucesso.")
        return redirect("pipelines:list")


class PipelineDeleteView(View):
    def post(self, request, pk: int):
        pipeline = get_object_or_404(PipelineDefinition, pk=pk)
        pipeline.delete()
        messages.success(request, "Pipeline excluído com sucesso.")
        return redirect("pipelines:list")

