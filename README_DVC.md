# DVC Pipeline Guide – Healthcare RAG Application

This document explains how to use [DVC (Data Version Control)](https://dvc.org)
to manage, reproduce and track the RAG pipeline stages.

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.10+ |
| DVC | 3.x (`pip install dvc`) |
| pip packages | See `rag_llm_app/requirements.txt` |

---

## Quick Start

```bash
# 1. Install DVC
pip install dvc

# 2. Install project dependencies
make deps          # or: pip install -r rag_llm_app/requirements.txt

# 3. Initialise DVC (already done – skip if .dvc/ exists)
dvc init

# 4. Copy and populate the environment file
cp .env.example .env   # then edit .env with your API keys / paths

# 5. Run the full pipeline
make repro         # or: dvc repro
```

---

## Pipeline Stages

The pipeline is defined in `dvc.yaml` and consists of the following stages:

| # | Stage | Description |
|---|-------|-------------|
| 1 | `install_dependencies` | Install Python dependencies |
| 2 | `ingest_documents` | Load PDF → chunk → embed → save CSV |
| 3 | `test_retrieval` | Smoke-test retrieval with sample queries |
| 4 | `demo_retrieval` | Run demo queries and produce a results report |
| 5 | `evaluate_pipeline` | Measure end-to-end pipeline performance |
| 6 | `generate_docs` | Generate a Markdown pipeline report |

Each stage lists its dependencies (`deps`), outputs (`outs`), and optional
metrics (`metrics`) so that DVC can determine which stages need re-running
when inputs change.

---

## Useful Commands

```bash
# Show pipeline status (which stages are outdated)
dvc status

# Visualise the dependency graph
dvc dag

# Reproduce only a specific stage (and its dependencies)
dvc repro <stage_name>

# Display tracked metrics
dvc metrics show

# Clean generated outputs
make clean

# Run only retrieval tests
make test

# Run demo queries
make demo
```

---

## Configuration

Pipeline parameters are stored in `params.yaml`.  Edit this file to
change PDF path, chunk size, embedding model, etc., then re-run
`dvc repro` to update only the affected downstream stages.

Key parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `pdf_path` | `data/documents/Human-Nutrition-*.pdf` | Source PDF |
| `chunking.sentences_per_chunk` | 20 | Sentences per chunk window |
| `chunking.sentence_overlap` | 2 | Overlap between consecutive chunks |
| `chunking.max_tokens` | 1300 | Hard token ceiling per chunk |
| `embedding.model` | `text-embedding-3-small` | Embedding model name |
| `retrieval.top_k` | 5 | Number of retrieved documents per query |

---

## Environment Variables

Create a `.env` file in the project root.  The following variables are
recognised by the application (all optional unless noted):

```dotenv
# Model backend: "local" | "api" | "gemini"  (default: local)
MODEL_BACKEND=local

# Local sentence-transformers model
LOCAL_EMBEDDING_MODEL=all-mpnet-base-v2
LOCAL_LLM_MODEL=sshleifer/tiny-gpt2

# OpenAI (required when MODEL_BACKEND=api)
OPENAI_API_KEY=sk-...

# Google Gemini (required when MODEL_BACKEND=gemini)
GEMINI_API_KEY=AI...

# Supabase (required when RETRIEVER_MODE=supabase)
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Retrieval mode: "local" | "supabase"  (default: local)
RETRIEVER_MODE=local
```

---

## Troubleshooting

**`FileNotFoundError: Local embeddings not found`**  
Run the ingestion stage first: `dvc repro ingest_documents`

**`CUDA requested but not available`**  
The application automatically falls back to CPU.  To force CPU, set
`EMBEDDING_DEVICE=cpu` and `LLM_DEVICE=cpu` in `.env`.

**Supabase upload skipped (dimension mismatch)**  
The local model produces 768-dimensional embeddings while the default
Supabase schema expects 1536 dimensions (OpenAI).  Either switch to
the OpenAI backend (`MODEL_BACKEND=api`) or update the Supabase table
schema to use `vector(768)`.
