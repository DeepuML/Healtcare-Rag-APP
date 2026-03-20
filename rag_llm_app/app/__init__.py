"""
RAG LLM Application Package

This package provides a complete Retrieval-Augmented Generation (RAG)
pipeline for healthcare and nutrition question answering. It supports
multiple backends (local, OpenAI API, Google Gemini) and storage
backends (local CSV, Supabase).

Submodules:
    config      - Application settings loaded from environment variables
    ingestion   - PDF loading and text chunking utilities
    embeddings  - Text embedding models (local, OpenAI, Gemini)
    retriever   - Vector similarity search (local torch, Supabase)
    llm         - Answer generation models (local, OpenAI, Gemini)
    pipeline    - End-to-end RAG pipeline combining all components
    vectorstore - Supabase vector database client
    utils       - Shared utilities (logging, etc.)
"""

__version__ = "1.0.0"
