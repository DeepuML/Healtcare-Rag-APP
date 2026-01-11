"""Gemini API Embedder using Google's Generative AI"""

import os
import logging
import numpy as np
from typing import List
import google.generativeai as genai

from app.config import settings
from app.utils import get_logger

logger = get_logger(__name__)


class GeminiEmbedder:
    """Embedder using Google Gemini API for text embeddings"""
    
    def __init__(self, model: str = None):
        """
        Initialize Gemini Embedder
        
        Args:
            model: Embedding model name (default: from settings)
        """
        self.model = model or settings.GEMINI_EMBEDDING_MODEL
        self.api_key = settings.GEMINI_API_KEY
        self.embedding_dimension = settings.GEMINI_EMBEDDING_DIMENSION
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Configure Gemini API
        genai.configure(api_key=self.api_key)
        
        logger.info(f"GeminiEmbedder initialized with model: {self.model}")
        logger.info(f"Embedding dimension: {self.embedding_dimension}")
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Embed a single text using Gemini
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding as numpy array
        """
        try:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_document"
            )
            embedding = np.array(result['embedding'], dtype=np.float32)
            return embedding
        except Exception as e:
            logger.error(f"Error embedding text: {e}")
            raise
    
    def embed_chunks(self, chunks: List[str], batch_size: int = 100) -> List[np.ndarray]:
        """
        Embed multiple text chunks using Gemini
        
        Args:
            chunks: List of text chunks to embed
            batch_size: Number of chunks to process at once (Gemini API batching)
            
        Returns:
            List of embeddings as numpy arrays
        """
        embeddings = []
        total = len(chunks)
        
        for i in range(0, total, batch_size):
            batch = chunks[i:i + batch_size]
            logger.info(f"Embedding batch {i//batch_size + 1}/{(total + batch_size - 1)//batch_size}")
            
            for chunk in batch:
                try:
                    embedding = self.embed_text(chunk)
                    embeddings.append(embedding)
                except Exception as e:
                    logger.error(f"Error embedding chunk: {e}")
                    # Add zero vector as fallback
                    embeddings.append(np.zeros(self.embedding_dimension, dtype=np.float32))
        
        logger.info(f"Successfully embedded {len(embeddings)} chunks")
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embeddings"""
        return self.embedding_dimension
