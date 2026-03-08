from __future__ import annotations

import csv
import json
from typing import Any, Dict, List

import pandas as pd
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from documents.models import Document
from experiments.models import Experiment
from .models import EvaluationResult


def document_dashboard(request: HttpRequest, document_id: int) -> HttpResponse:
    document = get_object_or_404(Document, pk=document_id)
    experiments = (
        document.experiments.select_related(
            "llm_model",
            "pipeline",
            "result",
            "evaluation",
        )
        .all()
    )

    return render(
        request,
        "evaluation/document_dashboard.html",
        {
            "document": document,
            "experiments": experiments,
        },
    )


def overall_dashboard(request: HttpRequest) -> HttpResponse:
    evaluations = EvaluationResult.objects.select_related(
        "experiment__llm_model",
        "experiment__pipeline",
    )

    rows: List[Dict[str, Any]] = []
    for ev in evaluations:
        exp: Experiment = ev.experiment
        result = getattr(exp, "result", None)
        rows.append(
            {
                "model": exp.llm_model.name,
                "pipeline": exp.pipeline.name,
                "precision": ev.precision,
                "f1_score": ev.f1_score,
                "runtime": getattr(result, "runtime_seconds", None),
            }
        )

    model_stats: List[Dict[str, Any]] = []
    pipeline_stats: List[Dict[str, Any]] = []

    if rows:
        df = pd.DataFrame(rows)
        model_stats = (
            df.groupby("model")[["precision", "f1_score", "runtime"]]
            .mean()
            .reset_index()
            .to_dict(orient="records")
        )
        pipeline_stats = (
            df.groupby("pipeline")[["precision", "f1_score", "runtime"]]
            .mean()
            .reset_index()
            .to_dict(orient="records")
        )

    context = {
        "model_stats": model_stats,
        "pipeline_stats": pipeline_stats,
        "model_stats_json": json.dumps(model_stats),
        "pipeline_stats_json": json.dumps(pipeline_stats),
    }
    return render(request, "evaluation/overall_dashboard.html", context)


def export_results_csv(request: HttpRequest) -> HttpResponse:
    """
    Exporta resultados de experimentos (incluindo métricas) em CSV.
    """
    evaluations = EvaluationResult.objects.select_related(
        "experiment__document",
        "experiment__llm_model",
        "experiment__pipeline",
        "experiment__result",
    )

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="experiment_results.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "experiment_id",
            "document",
            "llm_model",
            "pipeline",
            "human_tags",
            "generated_tags",
            "precision",
            "recall",
            "f1_score",
            "accuracy",
            "runtime_seconds",
            "num_tokens",
        ]
    )

    for ev in evaluations:
        exp = ev.experiment
        doc = exp.document
        result = getattr(exp, "result", None)
        writer.writerow(
            [
                exp.id,
                doc.file_name,
                exp.llm_model.name,
                exp.pipeline.name,
                doc.human_tags,
                getattr(result, "generated_tags", ""),
                ev.precision,
                ev.recall,
                ev.f1_score,
                ev.accuracy,
                getattr(result, "runtime_seconds", ""),
                getattr(result, "num_tokens", ""),
            ]
        )

    return response

