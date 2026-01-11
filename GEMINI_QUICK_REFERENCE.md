# Gemini Integration - Quick Reference

## 🚀 Quick Start (60 seconds)

### 1. Get API Key (1 min)

Visit: https://aistudio.google.com/app/apikey and copy your key

### 2. Update .env (30 seconds)

```env
MODEL_BACKEND=gemini
GEMINI_API_KEY=paste_your_key_here
```

### 3. Install & Test (30 seconds)

```bash
pip install google-generativeai
python rag_llm_app/test_gemini_integration.py
```

## 📚 Documentation Map

| Document                                 | Purpose                | When to Use         |
| ---------------------------------------- | ---------------------- | ------------------- |
| `GEMINI_SETUP_GUIDE.md`                  | Complete setup guide   | First time setup    |
| `GEMINI_INTEGRATION_SUMMARY.md`          | What changed overview  | Understand changes  |
| `GEMINI_INTEGRATION_CHECKLIST.md`        | Verification checklist | Verify installation |
| `.env.example`                           | Configuration template | See all options     |
| `rag_llm_app/test_gemini_integration.py` | Test script            | Verify it works     |

## 💻 Code Examples

### Basic Usage

```python
from app.embeddings.factory import get_embedder
from app.llm.factory import get_generator

embedder = get_embedder()  # Gets GeminiEmbedder if MODEL_BACKEND=gemini
generator = get_generator()  # Gets GeminiGenerator if MODEL_BACKEND=gemini

# Embed text
embedding = embedder.embed_text("Your text here")

# Generate response
response = generator.generate("Your prompt here")

# Answer question
answer = generator.answer_question("Your question?", context="Context info")

# Summarize
summary = generator.summarize("Long text to summarize")
```

### With RAG Pipeline

```python
from app.pipeline.rag_pipeline import RAGPipeline

pipeline = RAGPipeline()  # Uses Gemini backend if configured
answer = pipeline.answer_question("What is machine learning?")
print(answer)
```

### Direct Usage

```python
from app.embeddings.gemini_embedder import GeminiEmbedder
from app.llm.gemini_generator import GeminiGenerator

embedder = GeminiEmbedder()
generator = GeminiGenerator(temperature=0.5, max_tokens=256)

embedding = embedder.embed_text("Hello")
response = generator.generate("Hello! How are you?")
```

## 🔧 Configuration Options

### Required (for Gemini)

```env
MODEL_BACKEND=gemini
GEMINI_API_KEY=your_key_here
```

### Optional (defaults shown)

```env
GEMINI_EMBEDDING_MODEL=models/embedding-001
GEMINI_EMBEDDING_DIMENSION=768
GEMINI_LLM_MODEL=gemini-2.0-flash
```

## 🎯 Available Models

### Embedding

- `models/embedding-001` (768-dim) - Recommended

### Text Generation

- `gemini-2.0-flash` - **Fastest** (default)
- `gemini-1.5-pro` - Highest quality
- `gemini-1.5-flash` - Balanced

## ⚙️ Switching Backends

Just change `MODEL_BACKEND` in `.env`:

```env
# Use Gemini
MODEL_BACKEND=gemini

# Or use OpenAI
# MODEL_BACKEND=api

# Or use Local models
# MODEL_BACKEND=local
```

No code changes needed!

## 🧪 Testing

```bash
# Full integration test
python rag_llm_app/test_gemini_integration.py

# Quick Python test
python -c "
from app.embeddings.factory import get_embedder
e = get_embedder()
embedding = e.embed_text('test')
print(f'Embedding dimension: {embedding.shape[0]}')
"
```

## ❌ Troubleshooting

| Issue             | Solution                                    |
| ----------------- | ------------------------------------------- |
| `Invalid API Key` | Check .env has correct key, no extra spaces |
| `Model not found` | Verify model names are correct              |
| `Quota exceeded`  | Free tier: 60 req/min, upgrade for more     |
| `Import error`    | Run `pip install google-generativeai`       |
| `Wrong dimension` | Should be 768 for models/embedding-001      |

## 📊 Performance Notes

- **Speed**: Very fast (API-based, no GPU needed)
- **Cost**: Free tier available (60 req/min)
- **Quality**: Excellent (comparable to GPT-4)
- **Setup**: Easy (just API key)
- **Internet**: Required

## 🔗 Useful Links

- API Key: https://aistudio.google.com/app/apikey
- API Docs: https://ai.google.dev/docs
- API Reference: https://ai.google.dev/api
- Models: https://ai.google.dev/models
- Pricing: https://ai.google.dev/pricing

## 📋 Checklist for First Time

- [ ] Got Gemini API key from aistudio.google.com
- [ ] Updated .env with MODEL_BACKEND=gemini
- [ ] Updated .env with GEMINI_API_KEY
- [ ] Installed google-generativeai: `pip install google-generativeai`
- [ ] Ran test: `python test_gemini_integration.py`
- [ ] All tests passed ✅
- [ ] Using in code via factory functions
- [ ] Optional: Read GEMINI_SETUP_GUIDE.md for advanced options

## 🎓 Architecture Pattern

The RAG app uses the **Factory Pattern** for backend abstraction:

```
Your Code
    ↓
Factory Functions (get_embedder, get_generator)
    ↓
Backend Selection (based on MODEL_BACKEND setting)
    ↓
Specific Implementation (GeminiEmbedder, GeminiGenerator, etc.)
    ↓
API/Service (Gemini, OpenAI, Local models)
```

This means: **Same code, different backends, just change config!**

## 📞 Support

For issues:

1. Check GEMINI_SETUP_GUIDE.md troubleshooting section
2. Check test output: `python test_gemini_integration.py`
3. See GEMINI_INTEGRATION_SUMMARY.md for overview
4. Reference Google API docs: https://ai.google.dev/docs

---

**Status**: ✅ Ready to use! Get your API key and start embedding & generating with Gemini!
