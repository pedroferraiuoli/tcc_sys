from __future__ import annotations

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .forms import BatchExperimentForm, ExperimentCreateForm
from .models import Experiment
from .services import run_batch_experiments, run_experiment


class ExperimentListView(View):
    def get(self, request):
        experiments = (
            Experiment.objects.select_related(
                "document",
                "llm_model",
                "pipeline",
                "result",
                "evaluation",
            )
            .all()
        )
        return render(
            request,
            "experiments/experiment_list.html",
            {"experiments": experiments},
        )


class ExperimentCreateView(View):
    def get(self, request):
        form = ExperimentCreateForm()
        return render(request, "experiments/experiment_create.html", {"form": form})

    def post(self, request):
        form = ExperimentCreateForm(request.POST)
        if not form.is_valid():
            return render(
                request,
                "experiments/experiment_create.html",
                {"form": form},
            )

        document = form.cleaned_data["document"]
        llm_model = form.cleaned_data["llm_model"]
        pipeline = form.cleaned_data["pipeline"]
        prompt = form.cleaned_data.get("prompt") or None

        experiment = Experiment.objects.create(
            document=document,
            llm_model=llm_model,
            pipeline=pipeline,
            prompt=prompt,
        )
        # Executa de forma síncrona
        run_experiment(experiment)
        messages.success(request, f"Experimento {experiment.pk} executado com sucesso.")
        return redirect("experiments:list")


class BatchExperimentView(View):
    def get(self, request):
        form = BatchExperimentForm()
        return render(request, "experiments/batch_experiment.html", {"form": form})

    def post(self, request):
        form = BatchExperimentForm(request.POST)
        if not form.is_valid():
            return render(
                request,
                "experiments/batch_experiment.html",
                {"form": form},
            )

        documents = form.cleaned_data["documents"]
        llm_models = form.cleaned_data["llm_models"]
        pipelines = form.cleaned_data["pipelines"]
        prompt = form.cleaned_data.get("prompt") or None

        run_batch_experiments(
            documents=documents,
            llm_models=llm_models,
            pipelines=pipelines,
            prompt=prompt,
        )
        messages.success(request, "Experimentos em lote executados com sucesso.")
        return redirect("experiments:list")

