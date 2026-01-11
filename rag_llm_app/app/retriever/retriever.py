"""Supabase retriever for similarity search"""

from typing import List, Dict
from supabase import create_client, Client
from app.config import settings
from app.utils import get_logger

logger = get_logger(__name__)


class SupabaseRetriever:
    """Retrieve relevant documents using vector similarity search"""
    
    def __init__(self):
        """Initialize Supabase client"""
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
        logger.info("SupabaseRetriever initialized")
    
    def create_search_function(self):
        """
        Create the RPC function for similarity search
        
        Run this SQL in Supabase SQL Editor:
        
        CREATE OR REPLACE FUNCTION match_documents (
            query_embedding vector(1536),
            match_threshold float DEFAULT 0.5,
            match_count int DEFAULT 5
        )
        RETURNS TABLE (
            id bigint,
            page_number integer,
            chunk_text text,
            chunk_char_count integer,
            chunk_word_count integer,
            chunk_token_count float,
            similarity float
        )
        LANGUAGE sql STABLE
        AS $$
            SELECT
                documents.id,
                documents.page_number,
                documents.chunk_text,
                documents.chunk_char_count,
                documents.chunk_word_count,
                documents.chunk_token_count,
                1 - (documents.embedding <=> query_embedding) AS similarity
            FROM documents
            WHERE 1 - (documents.embedding <=> query_embedding) > match_threshold
            ORDER BY documents.embedding <=> query_embedding
            LIMIT match_count;
        $$;
        """
        logger.warning(
            "Search function should be created via Supabase SQL Editor. "
            "See docstring for SQL command."
        )
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = None,
        similarity_threshold: float = 0.5
    ) -> List[Dict]:
        """
        Search for similar documents using vector similarity
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of matching documents with similarity scores
        """
        top_k = top_k or settings.TOP_K_RESULTS
        
        logger.info(f"Searching for top {top_k} similar documents...")
        
        try:
            result = self.client.rpc(
                'match_documents',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': similarity_threshold,
                    'match_count': top_k
                }
            ).execute()
            
            documents = result.data
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
        
        context_items = [doc['chunk_text'] for doc in documents]
        context = "- " + "\n- ".join(context_items)
        
        return context
