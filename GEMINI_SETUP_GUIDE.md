# Gemini API Setup Guide

This guide will help you set up and use Google Gemini API with the RAG LLM application.

## Prerequisites

- Google Cloud account
- Python 3.8+
- The RAG LLM application installed with dependencies

## Step 1: Get Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Get API Key"
3. Create a new API key in your Google Cloud project
4. Copy the API key (keep it confidential!)

## Step 2: Configure Environment Variables

Add the following to your `.env` file in the project root:

```env
# Switch to Gemini backend
MODEL_BACKEND=gemini

# Your Gemini API Key (from Step 1)
GEMINI_API_KEY=your_api_key_here

# Optional: Override default models
GEMINI_EMBEDDING_MODEL=models/embedding-001
GEMINI_EMBEDDING_DIMENSION=768
GEMINI_LLM_MODEL=gemini-2.0-flash
```

**Important:** Never commit your API key to version control. Use `.env` file with `*.env` in `.gitignore`.

## Step 3: Install Required Dependencies

The Gemini integration requires the Google Generative AI library:

```bash
pip install google-generativeai>=0.3.0
```

Or update your project dependencies:

```bash
pip install -r rag_llm_app/requirements.txt
```

Ensure `google-generativeai` is in `requirements.txt`:

```
google-generativeai>=0.3.0
```

## Step 4: Verify Configuration

Run the configuration validator to ensure everything is set up correctly:

```bash
python -m app.config.settings
```

Or in your Python code:

```python
from app.config import settings

# This will validate all settings on import
print(f"Model Backend: {settings.MODEL_BACKEND}")
print(f"Embedding Model: {settings.GEMINI_EMBEDDING_MODEL}")
print(f"LLM Model: {settings.GEMINI_LLM_MODEL}")
```

## Available Models

### Embedding Model

- **models/embedding-001** (768 dimensions)
  - Optimized for semantic search and retrieval
  - Cost-effective for production use
  - Recommended for RAG applications

### LLM Models

- **gemini-2.0-flash** (Recommended)

  - Fast inference speed
  - Good for real-time applications
  - Latest Gemini architecture
  - Default model in configuration

- **gemini-1.5-pro**

  - Higher quality responses
  - Slower than flash
  - Better for complex reasoning tasks
  - Use if you need higher accuracy

- **gemini-1.5-flash**
  - Balanced speed and quality
  - Good for most use cases
  - Lower cost than pro

To use a different model, update your `.env`:

```env
GEMINI_LLM_MODEL=gemini-1.5-pro
```

## Using Gemini in Your Code

### 1. Using the Factory Functions

The recommended way to use Gemini is through the factory functions:

```python
from app.embeddings.factory import get_embedder
from app.llm.factory import get_generator

# Get Gemini embedder and generator
embedder = get_embedder()  # Uses GEMINI backend based on settings
generator = get_generator()  # Uses GEMINI backend based on settings

# Embed text
embedding = embedder.embed_text("Hello world")
print(f"Embedding dimension: {embedding.shape[0]}")  # Should be 768

# Generate response
response = generator.generate("What is the capital of France?")
print(response)
```

### 2. Using the RAG Pipeline

The RAG pipeline automatically uses your configured backend:

```python
from app.pipeline.rag_pipeline import RAGPipeline

# Initialize pipeline (will use Gemini backend from settings)
pipeline = RAGPipeline()

# Ask a question
answer = pipeline.answer_question("What are the benefits of exercise?")
print(answer)
```

### 3. Direct Usage

You can also use Gemini classes directly:

```python
from app.embeddings.gemini_embedder import GeminiEmbedder
from app.llm.gemini_generator import GeminiGenerator

# Create instances
embedder = GeminiEmbedder()
generator = GeminiGenerator(temperature=0.7, max_tokens=512)

# Generate embeddings
chunks = ["First chunk", "Second chunk", "Third chunk"]
embeddings = embedder.embed_chunks(chunks)

# Generate text
answer = generator.answer_question(
    "What is machine learning?",
    context="Machine learning is a subset of AI..."
)
print(answer)
```

## API Limits and Quotas

Free tier includes:

- 60 requests per minute for embedding API
- 500 requests per day for text generation
- Fair use policy applies

For production use, consider upgrading to a paid plan for higher quotas.

## Troubleshooting

### Error: "Invalid API Key"

- Check your `.env` file has correct `GEMINI_API_KEY`
- Verify the key from Google AI Studio is not expired
- Remove any extra spaces from the key

### Error: "Model not found"

- Ensure `GEMINI_EMBEDDING_MODEL` and `GEMINI_LLM_MODEL` are correct
- Check the model names match available Gemini models
- Verify your API key has access to the selected model

### Error: "Quota exceeded"

- You've hit the rate limit (60 req/min or daily quota)
- Add delays between API calls
- Upgrade to a paid plan for higher quotas
- Consider batching requests

### Slow Response Times

- Check your internet connection
- The first request might be slower (model initialization)
- Consider using `gemini-2.0-flash` for faster inference
- Reduce `max_tokens` if generating very long responses

### Embeddings have wrong dimension

- Default should be 768 for `models/embedding-001`
- Check `GEMINI_EMBEDDING_DIMENSION` in `.env` or settings.py
- Verify `GEMINI_EMBEDDING_MODEL` is set correctly

## Performance Comparison

| Feature       | Local           | OpenAI    | Gemini    |
| ------------- | --------------- | --------- | --------- |
| Speed         | Slow (GPU)      | Fast      | Very Fast |
| Cost          | Free (hardware) | Per token | Per token |
| API Required  | No              | Yes       | Yes       |
| Quality       | Good            | Excellent | Very Good |
| Embedding Dim | 768             | 1536      | 768       |
| Setup         | Complex         | Easy      | Easy      |
| Internet      | Not needed      | Required  | Required  |

## Switching Backends

To switch between different backends, simply change `MODEL_BACKEND` in `.env`:

```env
# Use Gemini
MODEL_BACKEND=gemini

# Use OpenAI
# MODEL_BACKEND=api

# Use Local models (requires GPU)
# MODEL_BACKEND=local
```

The rest of your code doesn't need to change - the factory functions handle the switching.

## Next Steps

1. Update `.env` with your Gemini API key
2. Run `python rag_llm_app/test_retrieval.py` to test the integration
3. Check the logs to verify Gemini is being used
4. Integrate into your RAG pipeline

For more information, see:

- [Google AI Studio Documentation](https://ai.google.dev/docs)
- [Gemini API Documentation](https://ai.google.dev/api)
- [RAG Pipeline Documentation](./PIPELINE_ARCHITECTURE.md)
