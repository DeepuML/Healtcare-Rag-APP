# Healthcare Nutrition RAG Application

A production-ready Retrieval-Augmented Generation (RAG) system for answering nutrition and healthcare questions using local LLMs and vector embeddings.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Next.js](https://img.shields.io/badge/Next.js-16.1-black.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)

## Table of Contents

- [Problem Statement](#problem-statement)
- [Solution](#solution)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [DVC Pipeline](#dvc-pipeline)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## Problem Statement

Healthcare and nutrition information is vast, complex, and often scattered across multiple sources. Users face several challenges:

- **Information Overload**: Thousands of pages of medical literature are difficult to search manually
- **Context Loss**: Traditional search engines return links, not contextualized answers
- **Trust & Citations**: Users need verifiable sources for health-related information
- **Accessibility**: Medical jargon makes information hard to understand for general users
- **Privacy Concerns**: Sending health queries to third-party APIs raises privacy issues

## Solution

A **locally-hosted RAG system** that combines the power of Large Language Models with vector search to provide accurate, contextual answers with source citations:

### Key Benefits:

**Privacy-First**: All processing happens locally - no data sent to external APIs  
 **Cited Answers**: Every response includes source page numbers and excerpts  
 **Fast Retrieval**: Vector embeddings enable semantic search in milliseconds  
 **Conversational UI**: ChatGPT-style interface with persistent chat history  
 **Production-Ready**: DVC pipeline for reproducibility and version control  
 **Scalable**: Supports both local vector search and Supabase cloud storage

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│              (Next.js 16 + React + Tailwind CSS)                │
└───────────────────────────────┬─────────────────────────────────┘
                                │ HTTP/REST
┌───────────────────────────────▼─────────────────────────────────┐
│                      FastAPI Backend                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ LocalEmbedder│  │LocalRetriever│  │  LLM Generator│          │
│  │ (MPNet-v2)   │  │ (Cosine Sim) │  │ (Mistral-7B)  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└───────────────────────────────┬─────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼────────┐   ┌─────────▼────────┐   ┌─────────▼─────────┐
│ Local CSV      │   │  Supabase        │   │  DVC Pipeline     │
│ (1158 chunks)  │   │  (pgvector)      │   │  (Reproducibility)│
└────────────────┘   └──────────────────┘   └───────────────────┘
```

### End-to-End Request Flow

1. A user submits a prompt in the Next.js UI, which forwards the request to the FastAPI backend over REST.
2. FastAPI validates and normalizes the text, then invokes the MPNet-v2 local embedder to create the query vector.
3. The retriever performs cosine-similarity searches across local CSV chunks, Supabase pgvector, and optionally DVC-logged artifacts, merging and deduplicating the combined results.
4. A context packaging step scores the retrieved snippets, trims them to fit the prompt budget, and assembles the final prompt (system instructions, user query, curated context).
5. The Mistral-7B generator receives the prompt via its serving layer, streams tokens back to FastAPI, and exposes partial generations for responsiveness.
6. A post-processing module adds citations, applies optional PII redaction, and returns the formatted answer to the UI while FastAPI logs retrieval and generation metrics.

### Data Flow:

1. **Ingestion**: PDF → Text Extraction → Chunking → Embeddings → Vector Store
2. **Query**: User Question → Embedding → Vector Search → Top-K Chunks
3. **Generation**: Chunks + Question → LLM → Contextual Answer
4. **Response**: Answer + Sources → UI Display

---

## Features

### RAG Pipeline

- **Semantic Search**: 768-dimensional embeddings using `all-mpnet-base-v2`
- **Chunk Retrieval**: Top-5 most relevant text chunks per query
- **Context Window**: Optimized prompt with retrieved context
- **Source Attribution**: Page numbers and text excerpts for every answer

### Local LLM Processing

- **Model**: Mistral-7B-Instruct-v0.2 (4-bit quantized)
- **Privacy**: 100% local inference - no cloud API calls
- **Performance**: GPU acceleration (CUDA) for fast generation
- **Customizable**: Adjustable temperature, max tokens, and prompt templates

### ChatGPT-Style UI

- **Conversational Interface**: Multi-turn conversations with message history
- **Persistent Storage**: localStorage saves chat history across sessions
- **Markdown Support**: Rich text rendering with GitHub-flavored markdown
- **Source Display**: Collapsible accordion showing source excerpts
- **Export/Import**: Download/upload chat history as JSON
- **Responsive Design**: Mobile-friendly centered layout (max-w-3xl)

### DVC Pipeline

- **7 Automated Stages**: Data validation → Ingestion → Chunking → Embedding → Retrieval → Generation → Evaluation
- **Reproducibility**: Version-controlled datasets and model outputs
- **Dependency Tracking**: Automatic re-execution on data/code changes
- **Metrics Logging**: BLEU, ROUGE, and cosine similarity scores

### Dual Storage Options

- **Local CSV**: Fast file-based storage for development
- **Supabase**: Cloud-hosted PostgreSQL with pgvector extension

---

## Tech Stack

### Backend

| Component         | Technology                       | Version     |
| ----------------- | -------------------------------- | ----------- |
| **Language**      | Python                           | 3.10+       |
| **API Framework** | FastAPI                          | 0.100+      |
| **Server**        | Uvicorn                          | 0.30+       |
| **Embeddings**    | sentence-transformers            | 2.2+        |
| **LLM**           | transformers (HuggingFace)       | 4.40+       |
| **Vector Search** | torch, numpy                     | 2.0+, 1.24+ |
| **Database**      | Supabase (PostgreSQL + pgvector) | -           |
| **Pipeline**      | DVC                              | 3.0+        |

### Frontend

| Component      | Technology                  | Version |
| -------------- | --------------------------- | ------- |
| **Framework**  | Next.js (App Router)        | 16.1.1  |
| **Language**   | TypeScript                  | 5.0+    |
| **UI Library** | React                       | 19.2.3  |
| **Styling**    | Tailwind CSS                | 3.4+    |
| **Icons**      | Lucide React                | 0.562+  |
| **Markdown**   | react-markdown + remark-gfm | 10.1+   |

### Models

- **Embedding Model**: `all-mpnet-base-v2` (768 dimensions)
- **LLM**: `mistralai/Mistral-7B-Instruct-v0.2` (4-bit quantized)

---

## Prerequisites

### System Requirements

- **OS**: Windows 10/11, Linux, or macOS
- **RAM**: 16GB minimum (32GB recommended for LLM)
- **GPU**: NVIDIA GPU with 8GB+ VRAM (CUDA 11.8+) for optimal performance
- **Storage**: 20GB free disk space

### Software Dependencies

```bash
# Python
Python 3.10+
pip 23.0+

# Node.js
Node.js 18.0+
npm 9.0+

# Git & DVC
Git 2.30+
DVC 3.0+
```

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/DeepuML/Healtcare-Rag-APP.git
cd Healtcare-Rag-APP
```

### 2. Backend Setup

#### Create Virtual Environment

```bash
python -m venv rag
# Windows
rag\Scripts\activate
# Linux/Mac
source rag/bin/activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

**Core Dependencies:**

```
fastapi==0.100.0
uvicorn==0.30.0
sentence-transformers==2.2.2
transformers==4.40.0
torch==2.0.1
supabase==2.5.0
python-dotenv==1.0.0
pandas==2.0.0
dvc==3.0.0
```

#### Configure Environment

Create `.env` file in project root:

```env
# Supabase Configuration (Optional)
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# Model Configuration
EMBEDDING_MODEL=all-mpnet-base-v2
LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2
DEVICE=cuda  # or cpu

# API Configuration
API_HOST=127.0.0.1
API_PORT=8000
```

### 3. Frontend Setup

```bash
cd rag_ui
npm install
```

**Key Dependencies:**

```json
{
  "next": "16.1.1",
  "react": "19.2.3",
  "react-markdown": "^10.1.0",
  "lucide-react": "^0.562.0",
  "tailwindcss": "^3.4.19"
}
```

### 4. Download Models (First Run)

Models are downloaded automatically on first run:

- **Embedding Model**: ~420MB
- **LLM Model**: ~4.5GB (4-bit quantized)

Or pre-download:

```python
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer

# Download embedding model
SentenceTransformer('all-mpnet-base-v2')

# Download LLM
AutoModelForCausalLM.from_pretrained('mistralai/Mistral-7B-Instruct-v0.2')
AutoTokenizer.from_pretrained('mistralai/Mistral-7B-Instruct-v0.2')
```

---

## DVC Pipeline

### Pipeline Overview

The DVC pipeline consists of 7 stages that automate the entire RAG workflow:

```bash
# Initialize DVC (first time only)
dvc init

# Run entire pipeline
dvc repro

# Run specific stage
dvc repro <stage_name>
```

### Pipeline Stages

#### 1. **Validate Data** (`validate_data`)

- **Purpose**: Verify PDF file exists and is readable
- **Input**: `data/human-nutrition-text.pdf`
- **Output**: `outputs/data_validation_report.md`
- **Metrics**: File size, page count, validation status

#### 2. **Ingest Data** (`ingest_data`)

- **Purpose**: Extract text from PDF and save to CSV
- **Input**: PDF file
- **Output**: `rag_llm_app/data/documents/text_chunks_and_embeddings_df.csv`
- **Details**: Extracts text from 1208 pages

#### 3. **Chunk Text** (`chunk_text`)

- **Purpose**: Split text into semantic chunks
- **Input**: Extracted text
- **Output**: 1158 text chunks
- **Strategy**: Recursive character splitting with overlap
- **Params**: `chunk_size=1000`, `chunk_overlap=200`

#### 4. **Generate Embeddings** (`generate_embeddings`)

- **Purpose**: Create vector embeddings for each chunk
- **Model**: `all-mpnet-base-v2`
- **Output**: 768-dimensional vectors
- **Performance**: ~100 chunks/second on GPU

#### 5. **Retrieve Context** (`retrieve_context`)

- **Purpose**: Test retrieval system with sample queries
- **Input**: Embeddings + test questions
- **Output**: Top-5 relevant chunks per query
- **Metrics**: `outputs/retrieval_metrics.json`

#### 6. **Generate Answers** (`generate_answers`)

- **Purpose**: Generate answers using LLM
- **Model**: Mistral-7B-Instruct-v0.2
- **Input**: Questions + Retrieved chunks
- **Output**: `outputs/generated_answers.json`

#### 7. **Evaluate RAG** (`evaluate_rag`)

- **Purpose**: Calculate quality metrics
- **Metrics**:
  - BLEU score (n-gram overlap)
  - ROUGE score (recall-oriented)
  - Cosine similarity (semantic)
- **Output**: `outputs/evaluation_metrics.json`

### DVC Configuration Files

**`dvc.yaml`** - Pipeline definition:

```yaml
stages:
  validate_data:
    cmd: python validate_setup.py
    deps:
      - data/human-nutrition-text.pdf
    outs:
      - outputs/data_validation_report.md
  # ... (7 stages total)
```

**`params.yaml`** - Hyperparameters:

```yaml
chunk_size: 1000
chunk_overlap: 200
embedding_model: "all-mpnet-base-v2"
llm_model: "mistralai/Mistral-7B-Instruct-v0.2"
top_k: 5
temperature: 0.7
max_tokens: 512
```

### Running the Pipeline

```bash
# Full pipeline execution
dvc repro

# Check pipeline status
dvc status

# View pipeline DAG
dvc dag

# View metrics
dvc metrics show

# Pull data from remote storage
dvc pull
```

---

## Usage

### Starting the Backend

#### Method 1: Direct Python

```bash
python api_server.py
```

#### Method 2: Uvicorn CLI

```bash
uvicorn api_server:app --host 127.0.0.1 --port 8000
```

**Expected Output:**

```
2026-01-11 15:54:27 - INFO - INITIALIZING RAG API SERVER
2026-01-11 15:54:27 - INFO - Loading chunks from CSV...
2026-01-11 15:54:27 - INFO - Loaded 1158 chunks
2026-01-11 15:54:33 - INFO - LocalEmbedder initialized successfully
2026-01-11 15:54:58 - INFO - LocalLLMGenerator initialized successfully
2026-01-11 15:54:58 - INFO - RAG API SERVER READY
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**API Endpoints:**

- Health Check: `http://127.0.0.1:8000/health`
- Query Endpoint: `http://127.0.0.1:8000/api/query`

### Starting the Frontend

```bash
cd rag_ui
npm run dev
```

**Expected Output:**

```
▲ Next.js 16.1.1 (Turbopack)
- Local:        http://localhost:3000
- Network:      http://192.168.148.1:3000

✓ Ready in 873ms
```

**Access the UI:**
Open browser to `http://localhost:3000`

### Testing the System

#### 1. Health Check

```bash
curl http://127.0.0.1:8000/health
# Response: {"status": "healthy"}
```

#### 2. API Query (PowerShell)

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://localhost:8000/api/query `
  -ContentType 'application/json' `
  -Body '{"question":"What is protein?"}' `
| ConvertTo-Json -Depth 4
```

#### 3. API Query (Bash/curl)

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What is protein?"}'
```

**Example Response:**

```json
{
  "answer": "Protein is one of the three macronutrients essential for human health...",
  "sources": [
    {
      "page": 145,
      "source": "Proteins are large biomolecules consisting of amino acids..."
    },
    {
      "page": 147,
      "source": "The recommended daily intake of protein is 0.8g per kg..."
    }
  ],
  "processing_time": 3.45
}
```

### Using the UI

1. **Ask Questions**: Type nutrition-related questions in the input box
2. **View Answers**: See AI-generated responses with markdown formatting
3. **Check Sources**: Expand the sources panel to see page references
4. **Chat History**: Conversations are saved automatically in localStorage
5. **Export/Import**: Download or upload chat history via header buttons
6. **Clear Chat**: Remove all messages using the Clear button

---

## Project Structure

```
Healtcare-Rag-APP/
├── api_server.py                 # FastAPI backend entry point
├── dvc.yaml                      # DVC pipeline configuration
├── params.yaml                   # Pipeline hyperparameters
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (not in git)
├── .gitignore                    # Git ignore rules
│
├── rag_llm_app/                  # Core RAG application
│   ├── __init__.py
│   ├── __main__.py               # CLI entry point
│   ├── local_workflow.py         # Local pipeline orchestration
│   ├── main.py                   # Main execution script
│   │
│   ├── config/                   # Configuration
│   │   ├── settings.py           # App settings & environment vars
│   │   └── __init__.py
│   │
│   ├── embeddings/               # Embedding models
│   │   ├── embedder.py           # Base embedder interface
│   │   ├── local_embedder.py     # MPNet-v2 implementation
│   │   ├── factory.py            # Embedder factory pattern
│   │   └── __init__.py
│   │
│   ├── llm/                      # Language models
│   │   ├── generator.py          # Base generator interface
│   │   ├── local_generator.py    # Mistral-7B implementation
│   │   ├── factory.py            # LLM factory pattern
│   │   └── __init__.py
│   │
│   ├── retriever/                # Vector retrieval
│   │   ├── retriever.py          # Base retriever interface
│   │   ├── local_retriever.py    # Local vector search
│   │   ├── factory.py            # Retriever factory pattern
│   │   └── __init__.py
│   │
│   ├── ingestion/                # Data processing
│   │   ├── loader.py             # PDF text extraction
│   │   ├── chunker.py            # Text chunking logic
│   │   └── __init__.py
│   │
│   ├── pipeline/                 # RAG pipeline
│   │   ├── rag_pipeline.py       # End-to-end RAG flow
│   │   └── __init__.py
│   │
│   ├── vectorstore/              # Vector storage
│   │   ├── vectordb.py           # Supabase integration
│   │   └── __init__.py
│   │
│   ├── utils/                    # Utilities
│   │   ├── logger.py             # Logging configuration
│   │   └── __init__.py
│   │
│   └── data/documents/           # Data storage
│       └── text_chunks_and_embeddings_df.csv  # 1158 chunks + embeddings
│
├── rag_ui/                       # Next.js Frontend
│   ├── app/                      # Next.js App Router
│   │   ├── layout.tsx            # Root layout
│   │   ├── page.tsx              # Main chat page
│   │   ├── globals.css           # Global styles
│   │   └── api/rag/route.ts      # API proxy to backend
│   │
│   ├── components/chat/          # UI Components
│   │   ├── ChatLayout.tsx        # Layout wrapper
│   │   ├── ChatHeader.tsx        # Header with controls
│   │   ├── MessageList.tsx       # Message feed
│   │   ├── MessageBubble.tsx     # Individual messages
│   │   ├── MessageInput.tsx      # Text input area
│   │   ├── SourcesAccordion.tsx  # Collapsible sources
│   │   └── TypingIndicator.tsx   # Loading animation
│   │
│   ├── hooks/                    # React Hooks
│   │   └── useChat.ts            # Chat logic + localStorage
│   │
│   ├── types/                    # TypeScript Types
│   │   └── chat.ts               # Message & Source interfaces
│   │
│   ├── public/                   # Static assets
│   ├── package.json              # NPM dependencies
│   ├── tsconfig.json             # TypeScript config
│   ├── tailwind.config.ts        # Tailwind config
│   ├── postcss.config.js         # PostCSS config
│   └── next.config.ts            # Next.js config
│
├── outputs/                      # DVC Pipeline Outputs
│   ├── data_validation_report.md
│   ├── retrieval_metrics.json
│   ├── generated_answers.json
│   └── evaluation_metrics.json
│
└── data/                         # Source Data
    └── human-nutrition-text.pdf  # 1208-page nutrition textbook
```

---

## API Documentation

### Base URL

```
http://127.0.0.1:8000
```

### Endpoints

#### `GET /health`

Health check endpoint.

**Response:**

```json
{
  "status": "healthy"
}
```

---

#### `POST /api/query`

Submit a question to the RAG system.

**Request Body:**

```json
{
  "question": "What are the benefits of vitamin C?"
}
```

**Response:**

```json
{
  "answer": "Vitamin C, also known as ascorbic acid, provides several health benefits...",
  "sources": [
    {
      "page": 234,
      "source": "Vitamin C is a water-soluble vitamin that acts as an antioxidant..."
    },
    {
      "page": 236,
      "source": "The recommended daily intake of vitamin C is 75-90mg for adults..."
    }
  ],
  "processing_time": 2.87
}
```

**Error Response:**

```json
{
  "error": "An error occurred while processing your request",
  "detail": "Specific error message here"
}
```

**Status Codes:**

- `200`: Success
- `400`: Bad Request (missing question)
- `500`: Internal Server Error

---

## Configuration

### Environment Variables

Create `.env` file in project root:

```env
# ===== Supabase Configuration =====
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here

# ===== Model Configuration =====
EMBEDDING_MODEL=all-mpnet-base-v2
EMBEDDING_DIMENSION=768
LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2
DEVICE=cuda  # Options: cuda, cpu

# ===== API Configuration =====
API_HOST=127.0.0.1
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# ===== Generation Parameters =====
TEMPERATURE=0.7
MAX_TOKENS=512
TOP_K=5
TOP_P=0.9

# ===== Logging =====
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR
```

### DVC Parameters (`params.yaml`)

```yaml
# Text Chunking
chunk_size: 1000
chunk_overlap: 200
separator: "\n\n"

# Embedding
embedding_model: "all-mpnet-base-v2"
embedding_batch_size: 32

# Retrieval
top_k: 5
similarity_threshold: 0.7

# Generation
llm_model: "mistralai/Mistral-7B-Instruct-v0.2"
temperature: 0.7
max_tokens: 512
use_4bit: true

# Evaluation
eval_questions:
  - "What is protein?"
  - "How much water should I drink daily?"
  - "What are the benefits of vitamin D?"
```

### Next.js Configuration

**`.env.local`** (in `rag_ui/`):

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

---

## Deployment

### Backend Deployment Options

#### Option 1: Docker Container

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t healthcare-rag-backend .
docker run -p 8000:8000 healthcare-rag-backend
```

#### Option 2: Cloud VM (AWS/Azure/GCP)

- Deploy on GPU-enabled instance (e.g., AWS g4dn.xlarge)
- Install CUDA drivers and dependencies
- Run with systemd service

#### Option 3: Local Server

- Use `screen` or `tmux` for persistent sessions
- Set up Nginx reverse proxy
- Configure firewall rules

### Frontend Deployment Options

#### Option 1: Vercel (Recommended)

```bash
cd rag_ui
vercel deploy
```

#### Option 2: Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

#### Option 3: Static Export

```bash
npm run build
# Deploy /out folder to any static host
```

### Production Checklist

- [ ] Set environment variables
- [ ] Configure CORS origins
- [ ] Enable HTTPS/SSL
- [ ] Set up monitoring (e.g., Sentry)
- [ ] Configure rate limiting
- [ ] Set up logging aggregation
- [ ] Enable auto-scaling
- [ ] Configure backups for vector store
- [ ] Implement authentication (if needed)
- [ ] Set up CI/CD pipeline

---

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Run tests**
   ```bash
   pytest tests/
   ```
5. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
6. **Push to your branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Add tests for new features
- Update documentation
- Keep commits atomic and descriptive

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contact & Support

**Project Repository**: [https://github.com/DeepuML/Healtcare-Rag-APP](https://github.com/DeepuML/Healtcare-Rag-APP)

**Issues**: [GitHub Issues](https://github.com/DeepuML/Healtcare-Rag-APP/issues)

---

## Acknowledgments

- **Hugging Face**: For providing open-source transformer models
- **Mistral AI**: For the Mistral-7B-Instruct model
- **Supabase**: For the PostgreSQL + pgvector platform
- **Next.js Team**: For the amazing React framework
- **DVC**: For ML pipeline management and versioning
- **FastAPI**: For the high-performance Python web framework

---

## Performance Metrics

| Metric                  | Value                   |
| ----------------------- | ----------------------- |
| **Total Chunks**        | 1,158                   |
| **Embedding Dimension** | 768                     |
| **Average Query Time**  | 3-5 seconds             |
| **Retrieval Accuracy**  | Top-5 chunks            |
| **Model Size**          | 4.5GB (4-bit quantized) |
| **VRAM Usage**          | ~6GB                    |
| **Concurrent Users**    | 10+ (tested)            |

---

## Roadmap

- [x] Local RAG pipeline with DVC
- [x] Supabase vector store integration
- [x] FastAPI backend server
- [x] ChatGPT-style UI
- [x] Chat history persistence
- [ ] User authentication
- [ ] Multi-user support
- [ ] Document upload feature
- [ ] Fine-tuned domain-specific LLM
- [ ] Real-time streaming responses
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard

---

**Built with for Healthcare & Nutrition Education**
