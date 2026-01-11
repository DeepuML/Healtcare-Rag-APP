"""Supabase Vector Store client"""

from typing import List, Dict
from supabase import create_client, Client
from app.config import settings
from app.utils import get_logger

logger = get_logger(__name__)


class SupabaseVectorStore:
    """Handle vector storage and operations in Supabase"""
    
    def __init__(self):
        """Initialize Supabase client"""
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
        logger.info("SupabaseVectorStore initialized")
    
    def create_table(self, table_name: str = "documents"):
        """
        Create the documents table with vector support
        
        Note: This assumes pgvector extension is enabled in Supabase
        SQL to run in Supabase SQL Editor:
        
        CREATE EXTENSION IF NOT EXISTS vector;
        
        CREATE TABLE IF NOT EXISTS documents (
            id BIGSERIAL PRIMARY KEY,
            page_number INTEGER,
            chunk_text TEXT,
            chunk_char_count INTEGER,
            chunk_word_count INTEGER,
            chunk_token_count FLOAT,
            embedding vector(1536),
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
        
        Args:
            table_name: Name of the table
        """
        logger.warning(
            "Table creation should be done via Supabase SQL Editor. "
            "See docstring for SQL commands."
        )
    
    def insert_chunks(
        self, 
        chunks: List[Dict], 
        embeddings: List[List[float]],
        table_name: str = "documents"
    ) -> bool:
        """
        Insert chunks with their embeddings into Supabase
        
        Args:
            chunks: List of chunk dictionaries
            embeddings: List of embedding vectors
            table_name: Name of the table
            
        Returns:
            Success status
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        logger.info(f"Inserting {len(chunks)} chunks into Supabase...")
        
        # Prepare data for insertion
        data_to_insert = []
        for chunk, embedding in zip(chunks, embeddings):
            data_to_insert.append({
                "page_number": chunk["page_number"],
                "chunk_text": chunk["sentence_chunk"],
                "chunk_char_count": chunk["chunk_char_count"],
                "chunk_word_count": chunk["chunk_word_count"],
                "chunk_token_count": chunk["chunk_token_count"],
                "embedding": embedding
            })
        
        try:
            # Insert in batches of 100 to avoid payload size limits
            batch_size = 100
            for i in range(0, len(data_to_insert), batch_size):
                batch = data_to_insert[i:i + batch_size]
                self.client.table(table_name).insert(batch).execute()
                logger.info(f"Inserted batch {i//batch_size + 1}/{(len(data_to_insert) + batch_size - 1)//batch_size}")
            
            logger.info(f"Successfully inserted {len(chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Error inserting chunks: {e}")
            raise
    
    def count_documents(self, table_name: str = "documents") -> int:
        """
        Count total documents in the table
        
        Args:
            table_name: Name of the table
            
        Returns:
            Document count
        """
        try:
            result = self.client.table(table_name).select("id", count="exact").execute()
            count = result.count if hasattr(result, 'count') else 0
            logger.info(f"Total documents in {table_name}: {count}")
            return count
        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            return 0
