from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from django.conf import settings

from documents.models import Document
from llm.models import LLMModel, PromptTemplate
from llm.services import call_llm
from .models import PipelineDefinition, PipelineType

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Resultado padronizado de execução de pipeline."""

    tags_text: str
    runtime_seconds: float
    num_tokens_estimated: int


def _estimate_tokens(text: str) -> int:
    """Estimativa simples de número de tokens com base em palavras."""
    if not text:
        return 0
    return len(text.split())


def run_direct_pipeline(
    document: Document,
    llm_model: LLMModel,
    prompt: PromptTemplate,
) -> PipelineResult:
    """
    Pipeline baseline: texto extraído completo → prompt → LLM → tags.
    """
    logger.info(
        "Iniciando pipeline direto para documento %s com modelo %s",
        document.id,
        llm_model.name,
    )

    full_prompt = f"{prompt.text}\n\nTexto do documento:\n{document.extracted_text}"

    start = time.monotonic()
    tags_text = call_llm(llm_model, full_prompt)
    elapsed = time.monotonic() - start

    num_tokens = _estimate_tokens(full_prompt) + _estimate_tokens(tags_text)

    return PipelineResult(
        tags_text=tags_text,
        runtime_seconds=elapsed,
        num_tokens_estimated=num_tokens,
    )


def run_rag_pipeline(
    document: Document,
    llm_model: LLMModel,
    prompt: PromptTemplate,
    pipeline: PipelineDefinition,
) -> PipelineResult:
    """
    Pipeline RAG: texto → indexação semântica → retrieval → contexto → prompt → LLM.

    Implementado com LlamaIndex usando embeddings locais (HuggingFace) e LLM Ollama.
    """
    logger.info(
        "Iniciando pipeline RAG para documento %s com modelo %s (pipeline=%s)",
        document.id,
        llm_model.name,
        pipeline.name,
    )

    from llama_index.core import Document as LlamaDocument, Settings, VectorStoreIndex
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.llms.ollama import Ollama

    # Configuração global do LlamaIndex
    embed_model_name = getattr(
        settings,
        "EMBEDDING_MODEL_NAME",
        "BAAI/bge-small-en-v1.5",
    )

    Settings.embed_model = HuggingFaceEmbedding(model_name=embed_model_name)
    Settings.node_parser = SentenceSplitter(
        chunk_size=pipeline.chunk_size,
        chunk_overlap=100,
    )

    base_url = llm_model.endpoint or "http://localhost:11434"
    Settings.llm = Ollama(
        model=llm_model.name,
        request_timeout=150.0,
        base_url=base_url,
    )

    llama_doc = LlamaDocument(
        text=document.extracted_text,
        metadata={"document_id": str(document.id)},
    )

    start = time.monotonic()

    index = VectorStoreIndex.from_documents([llama_doc])
    query_engine = index.as_query_engine(similarity_top_k=pipeline.top_k)

    # Usamos o próprio prompt científico como "query" de alto nível.
    response = query_engine.query(prompt.text)
    elapsed = time.monotonic() - start

    tags_text = str(response).strip()
    num_tokens = _estimate_tokens(prompt.text) + _estimate_tokens(tags_text)

    return PipelineResult(
        tags_text=tags_text,
        runtime_seconds=elapsed,
        num_tokens_estimated=num_tokens,
    )


def run_pipeline(
    pipeline: PipelineDefinition,
    document: Document,
    llm_model: LLMModel,
    prompt: PromptTemplate,
) -> PipelineResult:
    """Despacha para o tipo correto de pipeline."""
    if pipeline.is_direct:
        return run_direct_pipeline(document=document, llm_model=llm_model, prompt=prompt)
    if pipeline.is_rag:
        return run_rag_pipeline(
            document=document,
            llm_model=llm_model,
            prompt=prompt,
            pipeline=pipeline,
        )
    raise ValueError(f"Tipo de pipeline não suportado: {pipeline.type}")

