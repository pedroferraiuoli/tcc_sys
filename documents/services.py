from __future__ import annotations

from typing import Tuple

import pdfplumber
from django.db import transaction

from .models import Document


def extract_text_from_pdf(file_path: str) -> Tuple[str, int]:
    """Extrai texto e número de páginas de um PDF."""
    text_parts: list[str] = []
    num_pages = 0

    with pdfplumber.open(file_path) as pdf:
        num_pages = len(pdf.pages)
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)

    full_text = "\n\n".join(text_parts).strip()
    return full_text, num_pages


@transaction.atomic
def create_document_from_upload(uploaded_file) -> Document:
    """
    Cria um Document a partir de um arquivo enviado, já com texto extraído.

    A view deve chamar esta função após receber o arquivo do formulário.
    """
    document = Document(file_name=uploaded_file.name, pdf_file=uploaded_file)
    document.save()  # salva para garantir que o arquivo exista em disco

    text, num_pages = extract_text_from_pdf(document.pdf_file.path)
    document.extracted_text = text
    document.num_pages = num_pages
    document.save(update_fields=["extracted_text", "num_pages"])

    return document


@transaction.atomic
def reextract_text(document: Document) -> Document:
    """Permite reprocessar o PDF e atualizar o texto extraído."""
    text, num_pages = extract_text_from_pdf(document.pdf_file.path)
    document.extracted_text = text
    document.num_pages = num_pages
    document.save(update_fields=["extracted_text", "num_pages"])
    return document

