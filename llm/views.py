from __future__ import annotations

from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.views import View

from .forms import LLMModelForm, PromptTemplateForm
from .models import LLMModel, PromptTemplate


class LLMModelListView(View):
    def get(self, request):
        models = LLMModel.objects.all().order_by("name")
        return render(
            request,
            "llm/model_list.html",
            {"models": models},
        )


class LLMModelCreateView(View):
    def get(self, request):
        form = LLMModelForm()
        return render(request, "llm/model_form.html", {"form": form})

    def post(self, request):
        form = LLMModelForm(request.POST)
        if not form.is_valid():
            return render(request, "llm/model_form.html", {"form": form})

        form.save()
        messages.success(request, "Modelo LLM criado com sucesso.")
        return redirect("llm:model_list")


class LLMModelUpdateView(View):
    def get(self, request, pk: int):
        llm_model = get_object_or_404(LLMModel, pk=pk)
        form = LLMModelForm(instance=llm_model)
        return render(
            request,
            "llm/model_form.html",
            {
                "form": form,
                "object": llm_model,
            },
        )

    def post(self, request, pk: int):
        llm_model = get_object_or_404(LLMModel, pk=pk)
        form = LLMModelForm(request.POST, instance=llm_model)
        if not form.is_valid():
            return render(
                request,
                "llm/model_form.html",
                {
                    "form": form,
                    "object": llm_model,
                },
            )

        form.save()
        messages.success(request, "Modelo LLM atualizado com sucesso.")
        return redirect("llm:model_list")


class LLMModelDeleteView(View):
    def post(self, request, pk: int):
        llm_model = get_object_or_404(LLMModel, pk=pk)
        llm_model.delete()
        messages.success(request, "Modelo LLM excluído com sucesso.")
        return redirect("llm:model_list")


class PromptTemplateListView(View):
    def get(self, request):
        prompts = PromptTemplate.objects.all().order_by("name")
        return render(
            request,
            "llm/prompt_list.html",
            {"prompts": prompts},
        )


class PromptTemplateCreateView(View):
    def get(self, request):
        form = PromptTemplateForm()
        return render(request, "llm/prompt_form.html", {"form": form})

    def post(self, request):
        form = PromptTemplateForm(request.POST)
        if not form.is_valid():
            return render(request, "llm/prompt_form.html", {"form": form})

        form.save()
        messages.success(request, "Prompt criado com sucesso.")
        return redirect("llm:prompt_list")


class PromptTemplateUpdateView(View):
    def get(self, request, pk: int):
        prompt = get_object_or_404(PromptTemplate, pk=pk)
        form = PromptTemplateForm(instance=prompt)
        return render(
            request,
            "llm/prompt_form.html",
            {
                "form": form,
                "object": prompt,
            },
        )

    def post(self, request, pk: int):
        prompt = get_object_or_404(PromptTemplate, pk=pk)
        form = PromptTemplateForm(request.POST, instance=prompt)
        if not form.is_valid():
            return render(
                request,
                "llm/prompt_form.html",
                {
                    "form": form,
                    "object": prompt,
                },
            )

        form.save()
        messages.success(request, "Prompt atualizado com sucesso.")
        return redirect("llm:prompt_list")


class PromptTemplateDeleteView(View):
    def post(self, request, pk: int):
        prompt = get_object_or_404(PromptTemplate, pk=pk)
        prompt.delete()
        messages.success(request, "Prompt excluído com sucesso.")
        return redirect("llm:prompt_list")

