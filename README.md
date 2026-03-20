# 🏥 Healthcare Nutrition RAG Application

> A production-ready **Retrieval-Augmented Generation (RAG)** system that answers nutrition and healthcare questions by combining semantic vector search with locally-run or cloud-hosted LLMs — all served through a clean FastAPI backend.

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![DVC](https://img.shields.io/badge/DVC-3.0%2B-945DD6.svg)](https://dvc.org/)
[![Hugging Face](https://img.shields.io/badge/🤗%20HuggingFace-Transformers-FFD21E.svg)](https://huggingface.co/)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [⚡ Quick Start](#-quick-start)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Data Ingestion](#-data-ingestion)
- [DVC Pipeline](#-dvc-pipeline)
- [Running the Application](#-running-the-application)
- [API Reference](#-api-reference)
- [Project Structure](#-project-structure)
- [Development Commands](#-development-commands)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

---

## 🔍 Overview

Healthcare and nutrition knowledge is buried across thousands of pages of medical literature. This project tackles that with a **RAG (Retrieval-Augmented Generation)** system that:

1. **Ingests** a 1,208-page nutrition textbook (PDF) — extracting, chunking, and embedding the text into a searchable vector store
2. **Retrieves** the most semantically relevant passages for any user question using cosine-similarity search
3. **Generates** a grounded, cited answer using a pluggable LLM backend (local Hugging Face model, OpenAI API, or Google Gemini)
4. **Serves** everything through a FastAPI REST API, ready for any frontend or client to consume

### Why This Project?

| Pain Point | How This Solves It |
|---|---|
| Information overload from medical literature | Semantic search surfaces only the relevant passages |
| Traditional search returns links, not answers | LLM generates a direct, contextual response |
| Unverifiable health information | Every answer cites the exact page number it came from |
| Privacy concerns with cloud health queries | Local inference mode keeps all data on your machine |
| Hard to reproduce ML experiments | DVC pipeline tracks all stages, params, and artifacts |

---

## ✨ Key Features

### 🔎 RAG Pipeline
- **Semantic Search**: 768-dimensional embeddings using `all-mpnet-base-v2` (sentence-transformers)
- **Sentence-level Chunking**: PDF pages split into overlapping sentence-based chunks (~20 sentences, 2-sentence overlap)
- **Top-K Retrieval**: Cosine similarity search returns the top 5 most relevant chunks per query
- **Source Attribution**: Every answer includes the exact page numbers it drew from

### 🤖 Flexible LLM Backends
- **`local`** — Run any Hugging Face causal LM on your own hardware (default: `sshleifer/tiny-gpt2`; swap in `mistralai/Mistral-7B-Instruct-v0.2`, `google/gemma-7b-it`, or any instruction-tuned model)
- **`api`** — Use OpenAI's API (default: `gpt-4-turbo-preview`) — no GPU required
- **`gemini`** — Use Google Gemini (default: `gemini-2.0-flash`) — fast and free-tier friendly

### 🗄️ Dual Vector Storage
- **Local CSV**: Fast file-based storage — no external services required for development
- **Supabase pgvector**: Cloud-hosted PostgreSQL with pgvector for production-scale retrieval

### 🔁 Reproducible ML Pipeline
- **DVC-managed stages**: Install → Ingest → Test Retrieval → Demo → Evaluate → Docs
- **Parameter tracking**: All hyperparameters in `params.yaml`
- **Artifact versioning**: Embeddings CSV and metrics are tracked and cached

### 🌐 REST API
- **FastAPI** backend with automatic OpenAPI docs at `/docs`
- **CORS-enabled** for easy frontend integration
- **Structured responses** with answer, sources, confidence, and processing time

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Client / Frontend                          │
│               (Any HTTP client · curl · Postman)                │
└───────────────────────────────┬─────────────────────────────────┘
                                │ HTTP/REST  (port 8000)
┌───────────────────────────────▼─────────────────────────────────┐
│                      FastAPI Backend                            │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ LocalEmbedder│  │LocalRetriever│  │     LLM Generator     │  │
│  │ (MPNet-v2)   │  │(Cosine Sim.) │  │ local / api / gemini  │  │
│  └──────────────┘  └──────────────┘  └───────────────────────┘  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
         ┌──────────────────────┼──────────────────────┐
         │                      │                      │
┌────────▼───────┐  ┌───────────▼──────────┐  ┌───────▼────────┐
│  Local CSV     │  │  Supabase pgvector   │  │  DVC Pipeline  │
│  (~1,680 chunks│  │  (cloud vector store)│  │ (versioning +  │
│   + embeddings)│  │                      │  │  metrics)      │
└────────────────┘  └──────────────────────┘  └────────────────┘
```

### Request Lifecycle

```
User Query
    │
    ▼
1. [Embed]       Query → 768-dim vector via all-mpnet-base-v2
    │
    ▼
2. [Retrieve]    Cosine similarity search → Top-5 relevant text chunks
    │
    ▼
3. [Prompt]      Assemble RAG prompt: system instructions + context + query
    │
    ▼
4. [Generate]    LLM (local / OpenAI / Gemini) → natural-language answer
    │
    ▼
5. [Respond]     JSON: { answer, sources[ { page, source } ], processing_time }
```

### Data Ingestion Flow

```
PDF (1,208 pages)
    │
    ├─► PyMuPDF text extraction (per page)
    │
    ├─► Text cleaning (whitespace normalisation, hyphen repair)
    │
    ├─► Sentence chunking (20 sentences/chunk, 2-sentence overlap)
    │       → ~1,680 chunks, 50–1,300 tokens each
    │
    ├─► Local embedding (all-mpnet-base-v2, 768-dim)
    │
    └─► Storage
            ├─ Local CSV: rag_llm_app/data/documents/text_chunks_and_embeddings_df.csv
            └─ Supabase: chunks table (if credentials provided)
```

---

## 🛠️ Tech Stack

### Backend

| Component | Technology | Version |
|---|---|---|
| **Language** | Python | 3.10+ |
| **API Framework** | FastAPI | 0.109+ |
| **ASGI Server** | Uvicorn | 0.27+ |
| **PDF Parsing** | PyMuPDF (fitz) | 1.23+ |
| **Embeddings** | sentence-transformers | 2.5+ |
| **Local LLM** | transformers (Hugging Face) | 4.36+ |
| **Quantization** | bitsandbytes | 0.43+ |
| **Tensor Ops** | PyTorch | 2.2+ |
| **Data Storage** | Supabase (PostgreSQL + pgvector) | 2.10+ |
| **Token Counting** | tiktoken | latest |
| **ML Pipeline** | DVC | 3.0+ |
| **Config Mgmt** | python-dotenv | 1.0+ |

### AI / Model Backends

| Backend | Embedding Model | LLM Model | Notes |
|---|---|---|---|
| **local** | `all-mpnet-base-v2` (768-dim) | Any Hugging Face causal LM | Requires GPU for large models |
| **api** | `text-embedding-3-small` (1536-dim) | `gpt-4-turbo-preview` | Requires `OPENAI_API_KEY` |
| **gemini** | `models/embedding-001` (768-dim) | `gemini-2.0-flash` | Requires `GEMINI_API_KEY` |

### Recommended Local LLMs (for production quality)

| Model | Size | VRAM | Notes |
|---|---|---|---|
| `sshleifer/tiny-gpt2` | ~50MB | <1 GB | Default — fast, for testing only |
| `mistralai/Mistral-7B-Instruct-v0.2` | ~4.5 GB (4-bit) | ~6 GB | High quality, recommended |
| `google/gemma-7b-it` | ~4.5 GB (4-bit) | ~6 GB | Google's instruction-tuned model |
| `meta-llama/Llama-2-7b-chat-hf` | ~4.5 GB (4-bit) | ~6 GB | Requires Hugging Face token |

---

## ⚡ Quick Start

Get the API running in under 5 minutes:

```bash
# 1. Clone the repository
git clone https://github.com/DeepuML/Healtcare-Rag-APP.git
cd Healtcare-Rag-APP

# 2. Create and activate a virtual environment
python -m venv rag
source rag/bin/activate        # Linux / macOS
# rag\Scripts\activate         # Windows

# 3. Install Python dependencies
pip install -r rag_llm_app/requirements.txt

# 4. Create your .env file (minimum config for local mode)
cat > .env << 'EOF'
MODEL_BACKEND=local
LOCAL_LLM_MODEL=sshleifer/tiny-gpt2
LOCAL_EMBEDDING_MODEL=all-mpnet-base-v2
RETRIEVER_MODE=local
EOF

# 5. Ingest the PDF (place your PDF at the path below first)
#    PDF path: rag_llm_app/data/documents/Human-Nutrition-2020-Edition-1598491699.pdf
python ingest.py

# 6. Start the API server
python api_server.py
```

The API is now live at **http://localhost:8000**

```bash
# Test it!
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are macronutrients?"}'
```

> 💡 **No GPU?** The default `sshleifer/tiny-gpt2` model runs on CPU. For better answer quality, set `LOCAL_LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2` (requires a GPU with ≥6 GB VRAM), or use the `api` / `gemini` backends instead.

---

## 📦 Prerequisites

### System Requirements

| Requirement | Minimum | Recommended |
|---|---|---|
| **OS** | Windows 10, Linux, macOS | Ubuntu 22.04 LTS |
| **Python** | 3.10 | 3.11 |
| **RAM** | 8 GB | 32 GB |
| **GPU VRAM** | None (CPU mode) | 8+ GB NVIDIA (for local LLMs) |
| **Disk Space** | 5 GB | 20+ GB |
| **CUDA** | — | 11.8+ (for GPU acceleration) |

### Required Software

```bash
# Verify installed versions
python --version    # 3.10+
pip --version       # 23.0+
git --version       # 2.30+

# Optional: DVC for pipeline management
pip install dvc
dvc --version       # 3.0+
```

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/DeepuML/Healtcare-Rag-APP.git
cd Healtcare-Rag-APP
```

### 2. Create a Virtual Environment

```bash
python -m venv rag

# Activate on Linux / macOS
source rag/bin/activate

# Activate on Windows
rag\Scripts\activate
```

### 3. Install Python Dependencies

```bash
# Core project dependencies (inside rag_llm_app/)
pip install -r rag_llm_app/requirements.txt
```

**What gets installed:**

```
# Core
python-dotenv==1.0.0    # Environment variable management
fastapi>=0.109.0        # REST API framework
uvicorn>=0.27.0         # ASGI server

# PDF Processing
PyMuPDF==1.23.26        # PDF text extraction

# ML / Embeddings
torch>=2.2.0            # Tensor operations
sentence-transformers>=2.5.0  # Local embedding model
transformers>=4.36.0    # Hugging Face model loading
accelerate>=0.27.0      # Efficient model loading
bitsandbytes>=0.43.0    # 4-bit quantization

# Data
pandas==2.2.0           # CSV/dataframe operations
numpy>=1.26.0           # Numerical operations
tiktoken                # Token counting

# Optional backends
supabase>=2.10.0        # Cloud vector store
openai>=1.12.0          # OpenAI API backend
google-generativeai>=0.3.0  # Gemini API backend

# Testing
pytest>=7.0.0
pytest-asyncio>=0.23.0
```

### 4. Add Your PDF Document

Place the nutrition PDF in the data directory:

```
rag_llm_app/data/documents/Human-Nutrition-2020-Edition-1598491699.pdf
```

> The PDF is not included in the repository due to its size. Download or source a copy of the [Human Nutrition (2020 Edition)](https://open.umn.edu/opentextbooks/textbooks/human-nutrition) open textbook.

### 5. Validate Setup

Run the setup validation script to check all dependencies:

```bash
python validate_setup.py
```

---

## ⚙️ Configuration

All configuration is done through environment variables loaded from a `.env` file in the project root.

### Create the `.env` File

```bash
cp .env.example .env   # if available, or create manually
```

### Full `.env` Reference

```env
# ===================================================================
# MODEL BACKEND SELECTION
# Options: "local" | "api" | "gemini"
# ===================================================================
MODEL_BACKEND=local

# ===================================================================
# LOCAL EMBEDDING (sentence-transformers)
# Used by all backends for ingestion and query embedding
# ===================================================================
LOCAL_EMBEDDING_MODEL=all-mpnet-base-v2   # 768-dim
LOCAL_EMBEDDING_DIMENSION=768
EMBEDDING_DEVICE=cpu                      # Options: cpu | cuda

# ===================================================================
# LOCAL LLM (Hugging Face) — only used when MODEL_BACKEND=local
# ===================================================================
LOCAL_LLM_MODEL=sshleifer/tiny-gpt2       # Default (for testing only)
# LOCAL_LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2  # Recommended
# LOCAL_LLM_MODEL=google/gemma-7b-it                  # Alternative
LLM_DEVICE=cuda                           # Options: cuda | cpu
USE_QUANTIZATION=false                    # true = 4-bit quant (GPU req.)
ATTENTION_IMPLEMENTATION=sdpa            # Options: sdpa | eager

# ===================================================================
# OPENAI API — only used when MODEL_BACKEND=api
# ===================================================================
OPENAI_API_KEY=sk-...
API_EMBEDDING_MODEL=text-embedding-3-small
API_EMBEDDING_DIMENSION=1536
API_LLM_MODEL=gpt-4-turbo-preview

# ===================================================================
# GOOGLE GEMINI — only used when MODEL_BACKEND=gemini
# ===================================================================
GEMINI_API_KEY=AIza...
GEMINI_EMBEDDING_MODEL=models/embedding-001
GEMINI_LLM_MODEL=gemini-2.0-flash

# ===================================================================
# RETRIEVER
# Options: "local" (CSV-based) | "supabase" (cloud pgvector)
# ===================================================================
RETRIEVER_MODE=local

# ===================================================================
# SUPABASE — only required when RETRIEVER_MODE=supabase
# ===================================================================
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# ===================================================================
# GENERATION PARAMETERS
# ===================================================================
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=512
TOP_K_RESULTS=5

# ===================================================================
# LOGGING
# Options: DEBUG | INFO | WARNING | ERROR
# ===================================================================
LOG_LEVEL=INFO
```

### DVC Parameters (`params.yaml`)

All pipeline hyperparameters are centralised in `params.yaml`:

```yaml
# Document path (used by ingest_documents stage)
pdf_path: "data/documents/Human-Nutrition-2020-Edition-1598491699.pdf"

# Chunking configuration
chunking:
  sentences_per_chunk: 20
  sentence_overlap: 2
  max_tokens: 1300
  min_tokens: 50

# Embedding configuration
embedding:
  model: "text-embedding-3-small"
  batch_size: 100

# Retrieval configuration
retrieval:
  top_k: 5
  similarity_threshold: 0.7

# Generation configuration
generation:
  temperature: 0.7
  max_tokens: 512
```

---

## 📄 Data Ingestion

The `ingest.py` script processes the source PDF and populates the vector store:

```bash
# Run data ingestion
python ingest.py
```

**What it does:**

1. **Opens** the PDF with PyMuPDF (page by page)
2. **Cleans** each page's text — fixes line breaks, normalises whitespace, repairs hyphenated words
3. **Chunks** text using a sliding window of 20 sentences with a 2-sentence overlap
4. **Filters** chunks shorter than 50 tokens (headings, page numbers, etc.)
5. **Embeds** all chunks using `LocalEmbedder` (`all-mpnet-base-v2`)
6. **Saves** chunks + embeddings to `rag_llm_app/data/documents/text_chunks_and_embeddings_df.csv`
7. **Uploads** to Supabase (if `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set in `.env`)

**Expected output:**

```
Reading PDF by pages...
📄 Loaded 1208 pages from PDF
Chunking (20 sentences per chunk, 2 overlap, min 50 tokens)...
✅ Built 1680 chunks from 1208 pages
   - Pages with text: 1187
   - Empty pages skipped: 21
Generating embeddings with local model (all-mpnet-base-v2)...
✅ Saved 1680 chunks to rag_llm_app/data/documents/text_chunks_and_embeddings_df.csv
🎉 Done! Processed 1680 chunks
```

> **Note on Supabase dimensions**: The local `all-mpnet-base-v2` model produces 768-dim embeddings. If your Supabase table was created for OpenAI's 1536-dim embeddings, the upload will be skipped automatically with a warning. Use `RETRIEVER_MODE=local` to bypass Supabase entirely.

---

## 🔁 DVC Pipeline

[DVC (Data Version Control)](https://dvc.org/) manages the ML pipeline, tracking dependencies between stages and enabling reproducible runs.

### Pipeline Overview

```
install_dependencies
       │
       ▼
ingest_documents  ──► text_chunks_and_embeddings_df.csv
       │
       ├──► test_retrieval  ──► outputs/retrieval_test_results.txt
       │
       ├──► demo_retrieval  ──► outputs/demo_results.txt
       │                        outputs/retrieval_metrics.json
       │
       ├──► evaluate_pipeline ──► outputs/pipeline_metrics.json
       │
       └──► generate_docs  ──► outputs/PIPELINE_REPORT.md
```

### Pipeline Stages

| Stage | Command | Output | Description |
|---|---|---|---|
| `install_dependencies` | `pip install -r rag_llm_app/requirements.txt` | — | Ensures all packages are installed |
| `ingest_documents` | `python -m app.local_workflow create <pdf_path>` | `text_chunks_and_embeddings_df.csv` | PDF → chunks + embeddings |
| `test_retrieval` | `python test_retrieval.py` | `retrieval_test_results.txt` | Validates retrieval with sample queries |
| `demo_retrieval` | `python demo_retrieval.py` | `demo_results.txt`, `retrieval_metrics.json` | Demo queries with metrics |
| `evaluate_pipeline` | `python pipeline_helpers.py evaluate_pipeline` | `pipeline_metrics.json` | End-to-end performance evaluation |
| `generate_docs` | `python pipeline_helpers.py generate_docs` | `PIPELINE_REPORT.md` | Auto-generates pipeline documentation |

### Running the Pipeline

```bash
# Initialize DVC (first time only)
dvc init

# Run the full pipeline
dvc repro

# Run a specific stage
dvc repro ingest_documents

# Check which stages are out of date
dvc status

# Visualise the pipeline DAG
dvc dag

# View tracked metrics
dvc metrics show

# Push artifacts to remote storage
dvc push

# Pull artifacts from remote storage
dvc pull
```

---

## ▶️ Running the Application

### Step 1 – Ingest the PDF (one-time)

```bash
python ingest.py
```

> Skip this step if `rag_llm_app/data/documents/text_chunks_and_embeddings_df.csv` already exists.

### Step 2 – Start the API Server

```bash
# Option A: run directly
python api_server.py

# Option B: via Uvicorn CLI (with hot-reload for development)
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

**Expected startup output:**

```
INFO - ================================================================================
INFO - INITIALIZING RAG API SERVER
INFO - ================================================================================
INFO - Loading chunks from rag_llm_app/data/documents/text_chunks_and_embeddings_df.csv
INFO - Loaded 1680 chunks
INFO - Embeddings tensor shape: torch.Size([1680, 768])
INFO - Initializing LocalEmbedder...
INFO - Initializing LocalRetriever...
INFO - Initializing LocalLLMGenerator...
INFO - ================================================================================
INFO - RAG API SERVER READY
INFO - ================================================================================
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 3 – Query the API

```bash
# Health check
curl http://localhost:8000/health

# Ask a nutrition question
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the fat-soluble vitamins?"}'
```

### Step 4 – Explore the Interactive API Docs

Open your browser to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📡 API Reference

### Base URL

```
http://localhost:8000
```

### Endpoints

---

#### `GET /`

Returns server information and available endpoints.

**Response `200`:**
```json
{
  "name": "RAG API Server",
  "version": "1.0.0",
  "endpoints": {
    "health": "/health",
    "query": "/api/query (POST)"
  }
}
```

---

#### `GET /health`

Health check — confirms the server is running and reports loaded components.

**Response `200`:**
```json
{
  "status": "healthy",
  "embedder": "all-mpnet-base-v2",
  "llm": "sshleifer/tiny-gpt2",
  "chunks_loaded": 1680
}
```

---

#### `POST /api/query`

Submit a natural-language question and receive an AI-generated answer with cited sources.

**Request Body:**
```json
{
  "question": "What are the benefits of vitamin C?"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `question` | `string` | ✅ | The nutrition/health question to answer |

**Response `200`:**
```json
{
  "answer": "Vitamin C, also known as ascorbic acid, is a water-soluble vitamin that acts as an antioxidant...",
  "sources": [
    {
      "page": 234,
      "source": "Page 234"
    },
    {
      "page": 236,
      "source": "Page 236"
    }
  ],
  "confidence": 0.8,
  "processing_time": 2.87
}
```

| Field | Type | Description |
|---|---|---|
| `answer` | `string` | LLM-generated answer grounded in retrieved context |
| `sources` | `array` | Page references for the retrieved chunks |
| `sources[].page` | `integer` | Page number in the source PDF |
| `sources[].source` | `string` | Label for the source chunk |
| `confidence` | `float` | Confidence score (0.0–1.0) |
| `processing_time` | `float` | Total query time in seconds |

**Error Response `400` — Missing question:**
```json
{
  "detail": "Question is required"
}
```

**Error Response `500` — Server error:**
```json
{
  "detail": "Query processing failed: <error message>"
}
```

**Status Codes:**

| Code | Meaning |
|---|---|
| `200` | Success |
| `400` | Bad request (empty question) |
| `500` | Internal server error |

### PowerShell Example

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://localhost:8000/api/query `
  -ContentType 'application/json' `
  -Body '{"question":"What is protein?"}' |
ConvertTo-Json -Depth 4
```

---

## 📁 Project Structure

```
Healtcare-Rag-APP/
│
├── api_server.py              # FastAPI application entry point
├── ingest.py                  # PDF ingestion script (PDF → CSV + Supabase)
├── validate_setup.py          # Setup validation / health check script
├── test_rag_output.py         # End-to-end RAG test (retrieval + generation)
├── setup_dvc.py               # Interactive DVC setup helper
├── run_dvc.bat                # Windows batch file for DVC pipeline
│
├── dvc.yaml                   # DVC pipeline stage definitions
├── dvc.lock                   # DVC lock file (auto-generated)
├── params.yaml                # Pipeline hyperparameters
├── Makefile                   # Convenience make targets
│
├── .env                       # 🔒 Environment variables (NOT in git)
├── .gitignore                 # Git ignore rules
├── .dvcignore                 # DVC ignore rules
│
├── rag_llm_app/               # Core application package
│   ├── requirements.txt       # Python dependencies
│   ├── demo_retrieval.py      # Demo script (DVC stage)
│   ├── test_retrieval.py      # Retrieval test script (DVC stage)
│   ├── test_gemini_integration.py  # Gemini backend integration test
│   │
│   ├── app/                   # Main Python package
│   │   ├── __init__.py
│   │   ├── __main__.py        # CLI entry point
│   │   ├── main.py            # Standalone execution script
│   │   ├── local_workflow.py  # Local pipeline orchestration (DVC stage)
│   │   │
│   │   ├── config/
│   │   │   └── settings.py    # Settings loaded from environment variables
│   │   │
│   │   ├── embeddings/
│   │   │   ├── embedder.py           # Abstract base class
│   │   │   ├── local_embedder.py     # sentence-transformers (all-mpnet-base-v2)
│   │   │   ├── gemini_embedder.py    # Google Gemini embedding backend
│   │   │   └── factory.py            # Factory: picks backend from MODEL_BACKEND
│   │   │
│   │   ├── llm/
│   │   │   ├── generator.py          # Abstract base class
│   │   │   ├── local_generator.py    # Hugging Face causal LM backend
│   │   │   ├── gemini_generator.py   # Google Gemini generation backend
│   │   │   └── factory.py            # Factory: picks backend from MODEL_BACKEND
│   │   │
│   │   ├── retriever/
│   │   │   ├── local_retriever.py    # Cosine similarity search over CSV embeddings
│   │   │   └── factory.py            # Factory: picks local or supabase retriever
│   │   │
│   │   ├── ingestion/
│   │   │   ├── loader.py      # PyMuPDF-based PDF loader
│   │   │   └── chunker.py     # Sentence-based text chunker
│   │   │
│   │   ├── pipeline/
│   │   │   └── rag_pipeline.py  # End-to-end RAG orchestration
│   │   │
│   │   ├── vectorstore/
│   │   │   └── vectordb.py    # Supabase pgvector integration
│   │   │
│   │   └── utils/
│   │       └── logger.py      # Structured logging configuration
│   │
│   ├── data/
│   │   └── documents/
│   │       ├── Human-Nutrition-2020-Edition-1598491699.pdf  # 🔒 Source PDF (not in git)
│   │       └── text_chunks_and_embeddings_df.csv           # Generated by ingest.py
│   │
│   └── outputs/               # DVC stage outputs
│       ├── retrieval_test_results.txt
│       ├── demo_results.txt
│       ├── retrieval_metrics.json
│       └── pipeline_metrics.json
│
├── outputs/                   # Top-level DVC outputs
│   └── PIPELINE_REPORT.md
│
└── rag_ui/                    # 🚧 Frontend (planned — directory reserved)
```

---

## 🔧 Development Commands

The `Makefile` provides shortcuts for common tasks:

```bash
make help           # Show all available targets

# Pipeline
make install        # Install DVC
make init           # Initialize DVC repository
make setup          # Run interactive setup script (setup_dvc.py)
make repro          # Run the full DVC pipeline (dvc repro)
make status         # Show which DVC stages are out of date
make dag            # Visualise the pipeline DAG
make metrics        # Display tracked metrics

# Development
make test           # Run retrieval tests only
make demo           # Run demo queries
make query          # Start interactive query mode
make report         # View the generated pipeline report

# Maintenance
make deps           # Install project Python dependencies
make clean          # Remove all DVC outputs and cached files
make quickstart     # install + init + setup (first-time setup)
```

---

## 🧪 Testing

### Validate Setup

```bash
# Check all required files, packages, and env vars
python validate_setup.py
```

### Test Retrieval (no LLM required)

```bash
# Test semantic search with sample queries
cd rag_llm_app
python test_retrieval.py
```

### End-to-End RAG Test

```bash
# Full test: PDF load → chunk → embed → retrieve
python test_rag_output.py
```

### Run DVC Test Stages

```bash
# Run only the retrieval test stage
dvc repro test_retrieval

# View results
cat rag_llm_app/outputs/retrieval_test_results.txt

# Run the demo stage
dvc repro demo_retrieval
cat outputs/demo_results.txt
```

### Test Gemini Integration

```bash
# Requires GEMINI_API_KEY in .env
cd rag_llm_app
python test_gemini_integration.py
```

### Manual API Test

```bash
# 1. Start the server
python api_server.py &

# 2. Health check
curl http://localhost:8000/health

# 3. Query
curl -s -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the role of carbohydrates in human nutrition?"}' \
  | python -m json.tool
```

---

## 🚢 Deployment

### Option 1 — Docker (Recommended)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY rag_llm_app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run the server
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t healthcare-rag-api .
docker run -p 8000:8000 \
  -e MODEL_BACKEND=gemini \
  -e GEMINI_API_KEY=your-key \
  -v $(pwd)/rag_llm_app/data:/app/rag_llm_app/data \
  healthcare-rag-api
```

### Option 2 — Cloud VM (AWS / Azure / GCP)

For production deployments with local LLMs:

1. **Provision a GPU instance** (e.g., AWS `g4dn.xlarge` — NVIDIA T4 16 GB VRAM)
2. **Install CUDA** 11.8+ and drivers
3. **Deploy the application**:
   ```bash
   git clone https://github.com/DeepuML/Healtcare-Rag-APP.git
   cd Healtcare-Rag-APP
   pip install -r rag_llm_app/requirements.txt
   cp .env.example .env  # edit with your config
   python ingest.py
   ```
4. **Run as a systemd service**:
   ```ini
   # /etc/systemd/system/rag-api.service
   [Unit]
   Description=Healthcare RAG API
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/Healtcare-Rag-APP
   ExecStart=/home/ubuntu/rag/bin/uvicorn api_server:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
   ```bash
   sudo systemctl enable rag-api
   sudo systemctl start rag-api
   ```

5. **Set up Nginx reverse proxy** with HTTPS (Let's Encrypt)

### Option 3 — Cloud API Backends (No GPU Required)

Use `MODEL_BACKEND=gemini` or `MODEL_BACKEND=api` to offload generation to a cloud API. This allows deployment on any basic VM or serverless platform with no GPU requirement.

### Production Checklist

- [ ] Set all required environment variables in `.env`
- [ ] Run `python ingest.py` to generate the embeddings CSV
- [ ] Configure CORS origins (`allow_origins` in `api_server.py`)
- [ ] Enable HTTPS / SSL (via Nginx or cloud load balancer)
- [ ] Set up log aggregation (e.g., CloudWatch, Datadog)
- [ ] Configure rate limiting (e.g., Nginx `limit_req`)
- [ ] Set up health-check monitoring
- [ ] Implement authentication if exposing publicly
- [ ] Back up the embeddings CSV (or use Supabase for durability)

---

## 🛠️ Troubleshooting

### `FileNotFoundError: CSV file not found`

The server cannot find the embeddings CSV. Run the ingestion first:
```bash
python ingest.py
```

---

### `CUDA requested but not available, falling back to CPU`

This is an informational warning, not an error. The app will continue on CPU. To suppress it, set `EMBEDDING_DEVICE=cpu` and `LLM_DEVICE=cpu` in your `.env`.

---

### LLM output is poor quality / nonsensical

The default model (`sshleifer/tiny-gpt2`) is a tiny model used for fast testing and produces poor answers. For meaningful results:

```env
# Option A: Use a real instruction-tuned model (requires ≥6 GB VRAM)
LOCAL_LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2
USE_QUANTIZATION=true
LLM_DEVICE=cuda

# Option B: Use Gemini (free tier, no GPU needed)
MODEL_BACKEND=gemini
GEMINI_API_KEY=your-gemini-api-key

# Option C: Use OpenAI
MODEL_BACKEND=api
OPENAI_API_KEY=sk-...
```

---

### `Supabase upload skipped: Table expects different embedding dimensions`

Your Supabase `chunks` table was likely created for OpenAI 1536-dim embeddings, but the local model produces 768-dim embeddings. Solutions:

1. **Use local storage** (recommended for development): set `RETRIEVER_MODE=local`
2. **Re-create the Supabase table** with `dimension=768`
3. **Use the API embedding backend**: set `MODEL_BACKEND=api` to use OpenAI's 1536-dim embeddings

---

### `ModuleNotFoundError: No module named 'app'`

The `api_server.py` adds `rag_llm_app` to the Python path automatically. If you're running scripts directly from inside `rag_llm_app/`, add the path manually:

```bash
cd rag_llm_app
PYTHONPATH=. python test_retrieval.py
```

---

### Port 8000 Already in Use

```bash
# Find the process using port 8000
lsof -i :8000        # Linux / macOS
netstat -ano | findstr :8000  # Windows

# Kill it (replace PID)
kill -9 <PID>

# Or run on a different port
uvicorn api_server:app --port 8001
```

---

### Out of Memory (GPU)

If you get CUDA OOM errors when loading a large model:

1. Enable 4-bit quantization: `USE_QUANTIZATION=true`
2. Use a smaller model (e.g., a 3B-parameter model)
3. Run on CPU: `LLM_DEVICE=cpu` (slower but no VRAM limit)
4. Use a cloud API backend instead

---

## ❓ FAQ

**Q: Do I need a GPU?**  
A: No. The default model (`sshleifer/tiny-gpt2`) runs on CPU. For better answers, use `MODEL_BACKEND=gemini` (free API) or `MODEL_BACKEND=api` (OpenAI). A GPU is only required for running large local models like Mistral-7B.

---

**Q: Can I use a different PDF / knowledge base?**  
A: Yes. Replace the PDF file and update the path in `params.yaml` and your `.env`:
```env
# In params.yaml
pdf_path: "data/documents/your-document.pdf"
```
Then re-run `python ingest.py` to rebuild the embeddings.

---

**Q: How many questions can it answer simultaneously?**  
A: The FastAPI server handles requests sequentially when using the local LLM (the model holds a GPU lock). For concurrent usage, use a cloud backend (`MODEL_BACKEND=api` or `gemini`) which supports parallel requests.

---

**Q: How accurate are the answers?**  
A: Accuracy depends on the LLM model. With `sshleifer/tiny-gpt2` (default), answers are poor — it's a testing model. With `Mistral-7B-Instruct-v0.2` or a cloud LLM, answers closely follow the source text. The retrieval step always finds the top-5 most relevant passages; the LLM quality determines how well it synthesises them.

---

**Q: Can I add my own documents to the knowledge base?**  
A: Currently, `ingest.py` processes a single PDF. You can extend it to loop over multiple PDFs or re-run it with a different file. A multi-document upload feature is on the roadmap.

---

**Q: Is there a frontend / UI?**  
A: The `rag_ui/` directory is reserved for a planned Next.js frontend. The backend REST API works with any HTTP client today. Contributions to build the frontend are welcome!

---

**Q: How do I update the knowledge base?**  
A: Replace or add to the source PDF, then re-run `python ingest.py`. If using DVC, run `dvc repro ingest_documents` to automatically re-run all downstream stages.

---

## 🗺️ Roadmap

### Completed ✅
- [x] PDF ingestion pipeline (PyMuPDF + sentence chunking)
- [x] Local embedding with `all-mpnet-base-v2`
- [x] Cosine similarity retrieval (local CSV)
- [x] FastAPI REST backend
- [x] Three LLM backends: local / OpenAI / Gemini
- [x] Supabase pgvector integration
- [x] DVC pipeline for reproducibility
- [x] Structured logging

### In Progress 🔄
- [ ] Next.js frontend UI (conversational chat interface)
- [ ] Multi-document ingestion support

### Planned 📋
- [ ] Streaming responses (Server-Sent Events)
- [ ] User authentication (JWT)
- [ ] Document upload via API
- [ ] Fine-tuned domain-specific LLM
- [ ] Advanced evaluation metrics (RAGAS, BLEU, ROUGE)
- [ ] Mobile app (React Native)
- [ ] Analytics dashboard

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
   ```bash
   # On GitHub: click Fork → create your fork
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**, following the guidelines below

4. **Test your changes**
   ```bash
   python validate_setup.py
   python test_rag_output.py
   ```

5. **Commit your changes** (use [Conventional Commits](https://www.conventionalcommits.org/))
   ```bash
   git commit -m "feat: add streaming response support"
   ```

6. **Push and open a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Coding Guidelines

| Area | Convention |
|---|---|
| **Python style** | PEP 8 — use `black` for formatting |
| **Type hints** | Required for all public functions |
| **Docstrings** | Google-style docstrings |
| **Tests** | Add `pytest` tests for new features |
| **Environment** | Never commit secrets or `.env` files |
| **Commits** | Conventional Commits format |

---

## 📊 Performance

| Metric | Value |
|---|---|
| **Source Document** | Human Nutrition (2020 Ed.), 1,208 pages |
| **Total Chunks** | ~1,680 |
| **Embedding Dimension** | 768 (local) · 1,536 (OpenAI API) |
| **Chunk Token Range** | 50–1,300 tokens |
| **Average Retrieval Time** | <100ms (cosine similarity, CPU) |
| **End-to-End Query Time** | 2–5s (cloud LLM) · 10–60s (local 7B, GPU) |
| **VRAM (Mistral-7B 4-bit)** | ~6 GB |

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [**Hugging Face**](https://huggingface.co/) — for the sentence-transformers library and open-source model hub
- [**Mistral AI**](https://mistral.ai/) — for the Mistral-7B-Instruct open-weight model
- [**Google**](https://deepmind.google/technologies/gemini/) — for the Gemini API
- [**Supabase**](https://supabase.com/) — for the open-source PostgreSQL + pgvector platform
- [**FastAPI**](https://fastapi.tiangolo.com/) — for the high-performance Python web framework
- [**DVC**](https://dvc.org/) — for ML pipeline management and data versioning
- [**PyMuPDF**](https://pymupdf.readthedocs.io/) — for robust PDF text extraction
- [**OpenStax**](https://openstax.org/) — for the open-access Human Nutrition textbook

---

## 📬 Contact & Support

**Repository**: [https://github.com/DeepuML/Healtcare-Rag-APP](https://github.com/DeepuML/Healtcare-Rag-APP)

**Issues & Bug Reports**: [GitHub Issues](https://github.com/DeepuML/Healtcare-Rag-APP/issues)

**Feature Requests**: Open a GitHub Issue with the `enhancement` label

---

*Built with ❤️ for Healthcare & Nutrition Education*
