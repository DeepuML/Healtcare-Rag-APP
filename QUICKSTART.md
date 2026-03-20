# Quick Start – Healthcare RAG Application

Get the RAG pipeline running in under five minutes.

---

## 1 – Clone and install

```bash
git clone https://github.com/DeepuML/Healtcare-Rag-APP.git
cd Healtcare-Rag-APP

# Install DVC
pip install dvc

# Install Python dependencies
pip install -r rag_llm_app/requirements.txt
```

---

## 2 – Configure the environment

```bash
# Copy the example env file (if provided) or create a new one
cp .env.example .env   # edit the values inside

# Minimum required setting for a fully local run:
echo "MODEL_BACKEND=local" >> .env
echo "RETRIEVER_MODE=local" >> .env
```

No API keys are needed for the default **local** backend.

---

## 3 – Add your PDF

Place the source PDF in `rag_llm_app/data/documents/`:

```bash
mkdir -p rag_llm_app/data/documents
cp /path/to/your-document.pdf rag_llm_app/data/documents/

# Update params.yaml to point at the file:
# pdf_path: "data/documents/your-document.pdf"
```

The repository is pre-configured for the *Human Nutrition (2020)*
textbook.  Adjust `params.yaml` for any other document.

---

## 4 – Run the pipeline

```bash
# Full pipeline (ingest → test → demo → evaluate → docs)
make repro

# --- or run individual stages ---

# Ingest PDF and create embeddings
dvc repro ingest_documents

# Test retrieval
make test

# Interactive query mode (no DVC)
make query
```

---

## 5 – Start the API server + UI

```bash
# Backend (FastAPI)
python api_server.py
# → Listening on http://localhost:8000

# Frontend (Next.js) – open a second terminal
cd rag_ui
npm install
npm run dev
# → Listening on http://localhost:3000
```

---

## What's Next?

| Goal | Command / File |
|------|---------------|
| Change embedding model | Edit `LOCAL_EMBEDDING_MODEL` in `.env` |
| Use OpenAI backend | Set `MODEL_BACKEND=api` and add `OPENAI_API_KEY` |
| Use Google Gemini | Set `MODEL_BACKEND=gemini` and add `GEMINI_API_KEY` |
| Store vectors in Supabase | Set `RETRIEVER_MODE=supabase` and add Supabase credentials |
| View full DVC docs | See [README_DVC.md](README_DVC.md) |
| Validate setup | `python validate_setup.py` |
