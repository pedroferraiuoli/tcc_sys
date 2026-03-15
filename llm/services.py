from __future__ import annotations

import logging
from typing import Optional

import requests
from django.db.models import QuerySet

from .models import LLMModel, PromptTemplate

logger = logging.getLogger(__name__)


def get_default_prompt() -> Optional[PromptTemplate]:
    """Retorna o prompt padrão (se existir)."""
    try:
        return PromptTemplate.objects.filter(is_default=True).earliest("created_at")
    except PromptTemplate.DoesNotExist:
        return None


def list_active_models() -> QuerySet[LLMModel]:
    """Retorna os modelos LLM ativos."""
    return LLMModel.objects.filter(is_active=True)


def call_llm(model: LLMModel, prompt: str, timeout: int = 60) -> str:
    """
    Faz a chamada ao modelo LLM configurado.

    Implementação básica para Ollama; outros providers podem ser adicionados.
    """
    if model.provider == LLMModel.Provider.OLLAMA:
        return _call_ollama(model, prompt, timeout=timeout)

    raise NotImplementedError(f"Provider LLM não suportado: {model.provider}")


def _call_ollama(model: LLMModel, prompt: str, timeout: int = 150) -> str:
    base_url = model.endpoint or "http://localhost:11434"
    url = f"{base_url.rstrip('/')}/api/generate"

    print(prompt)
    print(model.name)
    print(timeout)
    print(base_url)
    print(url)

    payload = {
        "model": model.name,
        "prompt": prompt,
        "stream": False,
        # Restringe a quantidade de texto gerado para evitar respostas
        # muito longas que estouram o tempo de requisição.
        "options": {
            "temperature": 0.2,
        },
    }

    logger.info("Chamando Ollama em %s com modelo %s", url, model.name)
    try:
        response = requests.post(url, json=payload, timeout=timeout)
        print(response.json())
        response.raise_for_status()
    except requests.Timeout as exc:  # type: ignore[reportAttributeAccessIssue]
        logger.exception("Timeout ao chamar Ollama em %s com modelo %s", url, model.name)
        raise RuntimeError(
            "Timeout ao chamar o modelo LLM via Ollama. "
            "Tente novamente com um documento menor ou verifique o serviço Ollama."
        ) from exc
    except requests.RequestException as exc:  # type: ignore[reportAttributeAccessIssue]
        logger.exception("Erro na requisição ao Ollama em %s com modelo %s", url, model.name)
        raise RuntimeError(
            "Falha na chamada ao modelo LLM via Ollama. Verifique se o serviço está ativo."
        ) from exc

    data = response.json()
    text = data.get("response", "") or ""
    return text.strip()

