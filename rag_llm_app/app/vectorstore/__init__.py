"""
Vector store subpackage.

Provides a client for inserting document chunks and their embedding
vectors into a Supabase (PostgreSQL + pgvector) database.

Exports:
    SupabaseVectorStore - High-level client for batch-inserting chunks
                          and querying document counts in Supabase.
"""

from .vectordb import SupabaseVectorStore

__all__ = ["SupabaseVectorStore"]
