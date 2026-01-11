"""Local retriever using torch for similarity search (matching notebook implementation)"""

from typing import List, Dict
import torch
from sentence_transformers import util
from time import perf_counter as timer
from app.config import settings
from app.utils import get_logger

logger = get_logger(__name__)


class LocalRetriever:
    """Retrieve relevant documents using local torch-based vector similarity search"""
    
    def __init__(self, embeddings: torch.Tensor = None, chunks: List[Dict] = None):
        """
        Initialize local retriever with embeddings
        
        Args:
            embeddings: Tensor of document embeddings
            chunks: List of chunk dictionaries matching the embeddings
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.embeddings = embeddings
        self.chunks = chunks
        
        if self.embeddings is not None:
            self.embeddings = self.embeddings.to(self.device)
            logger.info(f"LocalRetriever initialized with {len(self.embeddings)} embeddings on {self.device}")
    
    def load_embeddings(self, embeddings: torch.Tensor, chunks: List[Dict]):
        """
        Load embeddings and chunks after initialization
        
        Args:
            embeddings: Tensor of document embeddings
            chunks: List of chunk dictionaries
        """
        self.embeddings = embeddings.to(self.device)
        self.chunks = chunks
        logger.info(f"Loaded {len(self.embeddings)} embeddings")
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = None,
        print_time: bool = False
    ) -> List[Dict]:
        """
        Search for similar documents using dot product similarity
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            print_time: Whether to print search time
            
        Returns:
            List of matching documents with similarity scores
        """
        if self.embeddings is None or self.chunks is None:
            raise ValueError("Embeddings not loaded. Call load_embeddings() first.")
        
        top_k = top_k or settings.TOP_K_RESULTS
        
        logger.info(f"Searching for top {top_k} similar documents...")
        
        try:
            # Convert query embedding to tensor - ensure it's 2D (1, embedding_dim)
            if isinstance(query_embedding, list):
                query_embedding = torch.tensor(query_embedding, dtype=torch.float32)
            else:
                query_embedding = torch.tensor(query_embedding, dtype=torch.float32)
            
            # Ensure 2D: (batch_size=1, embedding_dim)
            if query_embedding.dim() == 1:
                query_embedding = query_embedding.unsqueeze(0)
            
            query_tensor = query_embedding.to(self.device)
            
            # Debug: check shapes and devices
            logger.info(f"Query tensor shape: {query_tensor.shape}, device: {query_tensor.device}")
            logger.info(f"Embeddings shape: {self.embeddings.shape}, device: {self.embeddings.device}")
            
            # Get dot product scores using matrix multiplication
            # query_tensor: (1, 768), embeddings: (1680, 768)
            # We want: (1, 1680) result - use element-wise multiplication and sum
            start_time = timer()
            # dot_scores = query @ embeddings.T = (1, 768) @ (768, 1680) = (1, 1680)
            dot_scores = torch.mm(query_tensor, self.embeddings.T)  
            dot_scores = dot_scores[0]  # Get first (and only) row: (1680,)
            end_time = timer()
            
            if print_time:
                logger.info(f"Time taken to get scores on {len(self.embeddings)} embeddings: {end_time-start_time:.5f} seconds.")
            
            # Get top k results
            scores, indices = torch.topk(input=dot_scores, k=top_k)
            
            # Convert to list of dicts
            documents = []
            for score, idx in zip(scores, indices):
                doc = self.chunks[idx.item()].copy()
                doc['similarity'] = score.item()
                doc['id'] = idx.item()
                documents.append(doc)
            
            logger.info(f"Found {len(documents)} matching documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            raise
    
    def format_context(self, documents: List[Dict]) -> str:
        """
        Format retrieved documents as context string
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant context found."
        
        context_items = [doc.get('sentence_chunk', doc.get('chunk_text', '')) for doc in documents]
        context = "- " + "\n- ".join(context_items)
        
        return context
