"""
Embeddings subpackage.

Provides text embedding models for converting raw text into dense
numeric vectors used by the retrieval stage.

Exports:
    OpenAIEmbedder - Embedder backed by the OpenAI Embeddings API.
    LocalEmbedder  - Embedder using a locally-running sentence-transformers model.
    get_embedder   - Factory function that selects the correct embedder
                     based on the ``MODEL_BACKEND`` setting.
"""

from .embedder import OpenAIEmbedder
from .local_embedder import LocalEmbedder
from .factory import get_embedder

__all__ = ["OpenAIEmbedder", "LocalEmbedder", "get_embedder"]
