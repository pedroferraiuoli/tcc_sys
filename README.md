# Sistema de Experimentos de Taggeamento de PDFs com LLMs

Este projeto Django implementa uma aplicação web para execução de experimentos de taggeamento automático de documentos PDF usando modelos de linguagem (LLMs), comparando:

- Pipeline 1: Extração direta de texto (baseline)
- Pipeline 2: RAG (Retrieval-Augmented Generation) com LlamaIndex

## Tecnologias principais

- Django
- SQLite (padrão) ou PostgreSQL
- PyMuPDF/pdfplumber para extração de texto (aqui usamos `pdfplumber`)
- LlamaIndex para RAG
- sentence-transformers ou embeddings via Ollama
- scikit-learn para cálculo de métricas
- pandas para agregação de resultados

## Estrutura de apps

- `documents` – upload de PDFs, extração de texto, definição de tags humanas
- `llm` – cadastro de modelos LLM e prompts
- `pipelines` – definição de pipelines (direto, RAG)
- `experiments` – execução de experimentos e armazenamento dos resultados
- `evaluation` – cálculo de métricas e dashboards

## Instalação rápida

Crie um ambiente virtual, instale dependências e aplique migrações:

```bash
cd tcc_sys
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Em seguida acesse `http://127.0.0.1:8000/`.

