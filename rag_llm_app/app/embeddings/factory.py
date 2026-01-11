"""Factory for creating embedders based on configuration"""

from app.config import settings
from app.utils import get_logger

logger = get_logger(__name__)


def get_embedder():
    """
    Factory function to get the appropriate embedder based on MODEL_BACKEND setting
    
    Returns:
        Embedder instance (LocalEmbedder, OpenAIEmbedder, or GeminiEmbedder)
    """
    backend = settings.MODEL_BACKEND
    
    logger.info(f"Creating embedder for backend: {backend}")
    
    if backend == "local":
        from .local_embedder import LocalEmbedder
        return LocalEmbedder()
    elif backend == "api":
        from .embedder import OpenAIEmbedder
        return OpenAIEmbedder()
    elif backend == "gemini":
        from .gemini_embedder import GeminiEmbedder
        return GeminiEmbedder()
    else:
        raise ValueError(
            f"Invalid MODEL_BACKEND: {backend}. Must be 'local', 'api', or 'gemini'"
        )
