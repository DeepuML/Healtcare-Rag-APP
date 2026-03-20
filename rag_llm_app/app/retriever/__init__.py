"""
Retriever subpackage.

Provides vector-similarity search back-ends that find the most
relevant text chunks for a given query embedding.

Exports:
    SupabaseRetriever - Retriever backed by pgvector similarity search
                        inside a Supabase (PostgreSQL) database.
    LocalRetriever    - Retriever using PyTorch dot-product similarity
                        search against an in-memory tensor of embeddings.
    get_retriever     - Factory function that selects the correct retriever
                        based on the ``RETRIEVER_MODE`` setting.
"""

from .retriever import SupabaseRetriever
from .local_retriever import LocalRetriever
from .factory import get_retriever

__all__ = ["SupabaseRetriever", "LocalRetriever", "get_retriever"]
