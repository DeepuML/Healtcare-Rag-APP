"""
Pipeline subpackage.

Wires together the embedder, retriever, and LLM generator into a
single end-to-end RAG (Retrieval-Augmented Generation) pipeline.

Exports:
    RAGPipeline - Orchestrates query embedding → document retrieval →
                  answer generation in a single ``query()`` call.
"""

from .rag_pipeline import RAGPipeline

__all__ = ["RAGPipeline"]
