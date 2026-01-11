"""Factory for creating retrievers"""

from typing import Optional
import torch
from app.utils import get_logger

logger = get_logger(__name__)


def get_retriever(mode: str = "supabase", embeddings: Optional[torch.Tensor] = None, chunks: Optional[list] = None):
    """
    Factory function to get the appropriate retriever
    
    Args:
        mode: "supabase" for cloud vector DB or "local" for torch-based search
        embeddings: Optional tensor of embeddings (for local mode)
        chunks: Optional list of chunks (for local mode)
    
    Returns:
        Retriever instance
    """
    logger.info(f"Creating retriever in mode: {mode}")
    
    if mode == "local":
        from .local_retriever import LocalRetriever
        return LocalRetriever(embeddings=embeddings, chunks=chunks)
    elif mode == "supabase":
        from .retriever import SupabaseRetriever
        return SupabaseRetriever()
    else:
        raise ValueError(f"Invalid retriever mode: {mode}. Must be 'local' or 'supabase'")
