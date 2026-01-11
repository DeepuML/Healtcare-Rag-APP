# RAG LLM Application

A production-ready Retrieval Augmented Generation (RAG) system that supports multiple backends: OpenAI, Google Gemini, and local models. Retrieves relevant documents and generates intelligent answers using embeddings and LLMs.

## 🏗️ Architecture

The system uses a modular, backend-agnostic architecture:

```
rag_llm_app/
│
├── app/
│   ├── main.py                  # CLI entry point
│   ├── config/
│   │   └── settings.py          # Environment configuration
│   ├── ingestion/
│   │   ├── loader.py            # PDF/document loading
│   │   └── chunker.py           # Text chunking strategies
│   ├── embeddings/
│   │   ├── factory.py           # Embedder factory (local/api/gemini)
│   │   ├── embedder.py          # OpenAI embeddings
│   │   ├── local_embedder.py    # Local embeddings (sentence-transformers)
│   │   └── gemini_embedder.py   # Google Gemini embeddings
│   ├── retriever/
│   │   └── retriever.py         # Similarity search
│   ├── llm/
│   │   ├── factory.py           # Generator factory (local/api/gemini)
│   │   ├── generator.py         # OpenAI text generation
│   │   ├── local_generator.py   # Local text generation
│   │   └── gemini_generator.py  # Google Gemini text generation
│   ├── vectorstore/
│   │   └── vectordb.py          # Vector database operations
│   ├── pipeline/
│   │   └── rag_pipeline.py      # End-to-end RAG workflow
│   └── utils/
│       └── logger.py            # Logging utilities
│
├── data/
│   └── documents/               # Place documents here
│
├── requirements.txt
├── .env
├── README.md
└── GEMINI_SETUP_GUIDE.md        # Google Gemini setup instructions
```

## 🚀 Setup

### 1. Install Dependencies

```bash
cd rag_llm_app
pip install -r requirements.txt
```

### 2. Configure Backend

Choose your backend by setting `MODEL_BACKEND` in `.env`:

#### Option A: Google Gemini (Recommended - Fast & Free)

```env
MODEL_BACKEND=gemini
GEMINI_API_KEY=your_api_key_here
# Optional: customize models
GEMINI_EMBEDDING_MODEL=models/embedding-001
GEMINI_LLM_MODEL=gemini-2.0-flash
```

See [GEMINI_SETUP_GUIDE.md](../GEMINI_SETUP_GUIDE.md) for detailed setup.

#### Option B: OpenAI (High Quality)

```env
MODEL_BACKEND=api
OPENAI_API_KEY=your_openai_api_key
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4-turbo-preview
```

#### Option C: Local Models (Free, Requires GPU)

```env
MODEL_BACKEND=local
# Models will use sentence-transformers and local LLM
```

Requires GPU with sufficient VRAM (8GB+ recommended).

### 3. Configure Vector Store (Optional)

## 📖 Usage

### Query with RAG Pipeline

The RAG pipeline automatically uses your configured backend:

```python
from app.pipeline.rag_pipeline import RAGPipeline

# Initialize pipeline (uses settings from .env)
pipeline = RAGPipeline()

# Ask questions
answer = pipeline.answer_question("What are macronutrients?")
print(answer)
```

### Using Different Backends

Switch backends by just changing `MODEL_BACKEND` in `.env`:

```python
from app.embeddings.factory import get_embedder
from app.llm.factory import get_generator

# Automatically uses configured backend
embedder = get_embedder()
generator = get_generator()

# Process data
embedding = embedder.embed_text("Sample text")
response = generator.generate("What is this about?")
```

### Command Line Interface

```bash
# Query the system (if CLI is implemented)
python -m app.main query

# Example interaction:
# Question: What are the benefits of exercise?
# Answer: [Generated response from your chosen backend]
The macronutrients include carbohydrates, lipids, and proteins. These are
essential nutrients that provide energy and support various bodily functions...

📚 Sources:
  [1] Page 5 (similarity: 0.892)
  [2] Page 12 (similarity: 0.854)
```

## 🔧 Configuration

Key settings in `.env`:

| Variable          | Description                 | Default                  |
| ----------------- | --------------------------- | ------------------------ |
| `EMBEDDING_MODEL` | OpenAI embedding model      | `text-embedding-3-small` |
| `LLM_MODEL`       | OpenAI chat model           | `gpt-4-turbo-preview`    |
| `CHUNK_SIZE`      | Sentences per chunk         | `10`                     |
| `TOP_K_RESULTS`   | Number of retrieval results | `5`                      |
| `LLM_TEMPERATURE` | Generation temperature      | `0.7`                    |

## 📊 Project Features

- ✅ **PDF Ingestion**: Robust PDF text extraction with PyMuPDF
- ✅ **Smart Chunking**: Sentence-based splitting with spaCy
- ✅ **Vector Storage**: Supabase pgvector for scalable storage
- ✅ **Semantic Search**: Fast similarity search with cosine distance
- ✅ **RAG Generation**: Context-aware answers with OpenAI
- ✅ **Logging**: Comprehensive logging throughout
- ✅ **Modular Design**: Easy to extend and customize

## 🧪 Testing

```bash
# Run tests (if implemented)
pytest tests/
```

## 📝 Example Queries

- "What are the fat-soluble vitamins?"
- "How does saliva help with digestion?"
- "What is the recommended protein intake per day?"
- "What are symptoms of pellagra?"

## 🔐 Security Notes

- Never commit `.env` file to version control
- Use service role key only in secure environments
- Rotate API keys regularly

## 🚧 Future Enhancements

- [ ] FastAPI REST API endpoint
- [ ] Streaming responses
- [ ] Multiple document support
- [ ] Hybrid search (keyword + semantic)
- [ ] Response evaluation metrics
- [ ] Web UI with Gradio/Streamlit

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.
