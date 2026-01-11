"""Complete RAG Pipeline connecting retrieval and generation"""

from typing import Dict, Optional
import ast
import numpy as np
import pandas as pd
import torch
from app.embeddings import get_embedder
from app.retriever import get_retriever
from app.llm import get_generator
from app.config import settings
from app.utils import get_logger

logger = get_logger(__name__)


class RAGPipeline:
    """End-to-end RAG pipeline supporting both local and API backends"""
    
    def __init__(self, retriever_mode: str = None, embeddings: Optional[torch.Tensor] = None, chunks: Optional[list] = None):
        """
        Initialize all components
        
        Args:
            retriever_mode: "supabase" for cloud DB or "local" for torch-based search
            embeddings: Optional preloaded embeddings (for local mode)
            chunks: Optional preloaded chunks (for local mode)
        """
        self.retriever_mode = retriever_mode or settings.RETRIEVER_MODE
        
        logger.info(f"Initializing RAG Pipeline with backend: {settings.MODEL_BACKEND}, retriever: {self.retriever_mode}")
        
        # Auto-load local embeddings when needed so downstream stages do not require manual wiring
        if self.retriever_mode == "local" and (embeddings is None or chunks is None):
            csv_path = settings.DOCUMENTS_DIR / "text_chunks_and_embeddings_df.csv"
            if not csv_path.exists():
                raise FileNotFoundError(
                    f"Local embeddings not found at {csv_path}. Run the local ingestion stage first."
                )
            df = pd.read_csv(csv_path)
            df["embedding"] = df["embedding"].apply(lambda x: np.array(ast.literal_eval(x), dtype=np.float32))
            chunks = df.to_dict(orient="records")
            embeddings = torch.tensor(np.array(df["embedding"].tolist()), dtype=torch.float32)
            logger.info(f"Loaded {len(chunks)} chunks for local retrieval from {csv_path}")
        
        self.embedder = get_embedder()
        self.retriever = get_retriever(mode=self.retriever_mode, embeddings=embeddings, chunks=chunks)
        self.generator = get_generator()
        
        logger.info("RAGPipeline initialized successfully")
    
    def query(
        self,
        question: str,
        top_k: int = None,
        return_context: bool = False
    ) -> str | Dict:
        """
        Answer a question using RAG
        
        Args:
            question: User question
            top_k: Number of context items to retrieve
            return_context: Whether to return context along with answer
            
        Returns:
            Answer string or dict with answer and context
        """
        logger.info(f"Processing query: {question}")
        
        # 1. Embed the query
        query_embedding = self.embedder.embed_text(question)
        
        # 2. Retrieve relevant documents
        documents = self.retriever.search(
            query_embedding=query_embedding,
            top_k=top_k
        )
        
        # 3. Format context
        context = self.retriever.format_context(documents)
        
        # 4. Generate answer
        answer = self.generator.generate(
            query=question,
            context=context
        )
        
        logger.info("Query processing complete")
        
        if return_context:
            return {
                "answer": answer,
                "context": documents,
                "context_text": context
            }
        
        return answer
