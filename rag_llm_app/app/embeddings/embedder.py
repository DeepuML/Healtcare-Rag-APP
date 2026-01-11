"""OpenAI Embedding wrapper"""

from typing import List
from openai import OpenAI
from tqdm import tqdm
from app.config import settings
from app.utils import get_logger

logger = get_logger(__name__)


class OpenAIEmbedder:
    """Create embeddings using OpenAI's API"""
    
    def __init__(self, model: str = None):
        """
        Initialize the embedder
        
        Args:
            model: OpenAI embedding model to use
        """
        self.model = model or settings.EMBEDDING_MODEL
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        logger.info(f"OpenAIEmbedder initialized with model: {self.model}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Create an embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return response.data[0].embedding
    
    def embed_chunks(self, chunks: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Create embeddings for multiple text chunks with batching
        
        Args:
            chunks: List of text chunks to embed
            batch_size: Number of texts to embed in each batch
            
        Returns:
            List of embedding vectors
        """
        logger.info(f"Embedding {len(chunks)} chunks...")
        
        all_embeddings = []
        
        # Process in batches
        for i in tqdm(range(0, len(chunks), batch_size), desc="Embedding batches"):
            batch = chunks[i:i + batch_size]
            
            try:
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.model
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
            except Exception as e:
                logger.error(f"Error embedding batch {i//batch_size + 1}: {e}")
                raise
        
        logger.info(f"Successfully created {len(all_embeddings)} embeddings")
        
        return all_embeddings
