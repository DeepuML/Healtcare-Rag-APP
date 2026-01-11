"""Local embedding using sentence-transformers (matching notebook implementation)"""

from typing import List
import torch
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from app.config import settings
from app.utils import get_logger

logger = get_logger(__name__)


class LocalEmbedder:
    """Create embeddings using sentence-transformers (local model)"""
    
    def __init__(self, model: str = None, device: str = None):
        """
        Initialize the local embedder
        
        Args:
            model: sentence-transformers model to use (e.g., all-mpnet-base-v2)
            device: Device to run model on ('cuda' or 'cpu')
        """
        self.model_name = model or settings.LOCAL_EMBEDDING_MODEL
        self.device = device or settings.EMBEDDING_DEVICE
        
        # Check CUDA availability
        if self.device == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA requested but not available, falling back to CPU")
            self.device = "cpu"
        
        logger.info(f"Loading local embedding model: {self.model_name} on {self.device}")
        
        self.model = SentenceTransformer(
            model_name_or_path=self.model_name,
            device=self.device
        )
        
        logger.info(f"LocalEmbedder initialized successfully")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Create an embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list
        """
        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
    
    def embed_chunks(self, chunks: List[str], batch_size: int = 32, show_progress: bool = True) -> List[List[float]]:
        """
        Create embeddings for multiple text chunks with batching
        
        Args:
            chunks: List of text chunks to embed
            batch_size: Number of texts to embed in each batch
            show_progress: Whether to show progress bar
            
        Returns:
            List of embedding vectors
        """
        logger.info(f"Embedding {len(chunks)} chunks with batch_size={batch_size}...")
        
        try:
            # Use sentence-transformers batching
            embeddings = self.model.encode(
                chunks,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_tensor=False
            )
            
            # Convert to list of lists
            if hasattr(embeddings, 'tolist'):
                embeddings = embeddings.tolist()
            else:
                embeddings = [list(emb) for emb in embeddings]
            
            logger.info(f"Successfully created {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error embedding chunks: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embeddings"""
        return self.model.get_sentence_embedding_dimension()
