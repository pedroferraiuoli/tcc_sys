from __future__ import annotations

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from .forms import DocumentTagsForm, DocumentUploadForm
from .models import Document
from .services import create_document_from_upload


class DocumentListView(View):
    def get(self, request):
        documents = Document.objects.all()
        return render(
            request,
            "documents/document_list.html",
            {"documents": documents},
        )


class DocumentUploadView(View):
    def get(self, request):
        form = DocumentUploadForm()
        return render(request, "documents/document_upload.html", {"form": form})

    def post(self, request):
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = form.cleaned_data["pdf_file"]
            document = create_document_from_upload(pdf_file)
            messages.success(request, "Documento enviado e texto extraído com sucesso.")
            return redirect("documents:detail", pk=document.pk)
        return render(request, "documents/document_upload.html", {"form": form})


class DocumentDetailView(View):
    def get(self, request, pk: int):
        document = get_object_or_404(Document, pk=pk)
        form = DocumentTagsForm(instance=document)
        return render(
            request,
            "documents/document_detail.html",
            {
                "document": document,
                "form": form,
            },
        )

    def post(self, request, pk: int):
        document = get_object_or_404(Document, pk=pk)
        form = DocumentTagsForm(request.POST, instance=document)
        if form.is_valid():
            form.save()
            messages.success(request, "Tags humanas atualizadas com sucesso.")
            return redirect("documents:detail", pk=document.pk)
        return render(
            request,
            "documents/document_detail.html",
            {
                "document": document,
                "form": form,
            },
        )


class DocumentDeleteView(View):
    def post(self, request, pk: int):
        document = get_object_or_404(Document, pk=pk)
        document.delete()
        messages.success(request, "Documento excluído com sucesso.")
        return redirect("documents:list")

