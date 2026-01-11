"""FastAPI server for RAG pipeline"""

import sys
import time
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
import pandas as pd
import numpy as np

# Add rag_llm_app to path
sys.path.insert(0, str(Path(__file__).parent / 'rag_llm_app'))

from app.config import settings
from app.embeddings import LocalEmbedder
from app.retriever import LocalRetriever
from app.llm import LocalLLMGenerator
from app.utils import get_logger

logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(title="RAG API", version="1.0.0")

# Add CORS middleware to allow requests from Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (or restrict to localhost:3000)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class QueryRequest(BaseModel):
    question: str

class Source(BaseModel):
    page: int
    source: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[Source] = []
    confidence: float | None = None
    processing_time: float | None = None

# Initialize components (loaded once at startup)
embedder: LocalEmbedder | None = None
retriever: LocalRetriever | None = None
llm_generator: LocalLLMGenerator | None = None
chunks_df: pd.DataFrame | None = None

@app.on_event("startup")
async def startup_event():
    """Initialize RAG components on startup"""
    global embedder, retriever, llm_generator, chunks_df
    
    try:
        logger.info("=" * 80)
        logger.info("INITIALIZING RAG API SERVER")
        logger.info("=" * 80)
        
        # Load embeddings and chunks from CSV
        csv_path = Path(__file__).parent / "rag_llm_app/data/documents/text_chunks_and_embeddings_df.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        logger.info(f"Loading chunks from {csv_path}")
        chunks_df = pd.read_csv(csv_path)
        logger.info(f"Loaded {len(chunks_df)} chunks")
        
        # Convert embeddings from string representation to numpy arrays
        embeddings_list = []
        for emb_str in chunks_df['embedding']:
            emb_array = np.array(eval(emb_str))
            embeddings_list.append(emb_array)
        
        embeddings_tensor = torch.tensor(
            np.array(embeddings_list),
            dtype=torch.float32
        )
        logger.info(f"Embeddings tensor shape: {embeddings_tensor.shape}")

        # Build chunks list for retriever
        chunks_list = []
        for _, row in chunks_df.iterrows():
            chunks_list.append({
                'sentence_chunk': row.get('sentence_chunk', ''),
                'page_number': int(row.get('page_number', 0)),
                # Optional source label for UI
                'source': f"Page {int(row.get('page_number', 0))}"
            })

        # Initialize components
        logger.info("Initializing LocalEmbedder...")
        embedder = LocalEmbedder()

        logger.info("Initializing LocalRetriever...")
        retriever = LocalRetriever(embeddings_tensor, chunks_list)

        logger.info("Initializing LocalLLMGenerator...")
        llm_generator = LocalLLMGenerator()
        
        logger.info("=" * 80)
        logger.info("RAG API SERVER READY")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Failed to initialize RAG components: {e}", exc_info=True)
        raise

@app.get("")
async def welcome():
    """Welcome endpoint"""
    return {"message": "welcome to the rag api server"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "embedder": "all-mpnet-base-v2",
        "llm": "tiny-gpt2",
        "chunks_loaded": len(chunks_df) if chunks_df is not None else 0,
    }

@app.post("/api/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """RAG query endpoint"""
    
    if not request.question or request.question.strip() == "":
        raise HTTPException(status_code=400, detail="Question is required")
    
    start_time = time.time()
    
    try:
        logger.info(f"Processing query: {request.question}")
        
        if embedder is None or retriever is None or llm_generator is None:
            raise RuntimeError("RAG components not initialized")
        
        # 1. Embed the question
        logger.info("Embedding question...")
        question_embeddings = embedder.embed_chunks([request.question], batch_size=1)
        question_embedding = question_embeddings[0]  # Get the first (and only) embedding
        
        # 2. Retrieve relevant chunks using the search method
        logger.info("Retrieving relevant chunks...")
        top_k = 5
        retrieved_results = retriever.search(question_embedding, top_k=top_k)
        
        # Convert results to our response format
        retrieved_chunks = []
        for result in retrieved_results:
            retrieved_chunks.append({
                'content': result.get('sentence_chunk', ''),
                'page': int(result.get('page_number', 0)),
                'source': f"Page {result.get('page_number', 0)}",
            })
        
        logger.info(f"Retrieved {len(retrieved_chunks)} relevant chunks")
        
        # 3. Build context from retrieved chunks
        context_text = "\n\n---\n\n".join([
            chunk['content'] for chunk in retrieved_chunks
        ])
        
        # 4. Generate answer using LLM
        logger.info("Generating answer with LLM...")
        answer = llm_generator.generate(
            query=request.question,
            context=context_text
        )
        
        processing_time = time.time() - start_time
        logger.info(f"Query processed in {processing_time:.2f}s")
        
        # Build response
        sources = [
            Source(page=chunk['page'], source=chunk['source'])
            for chunk in retrieved_chunks
        ]
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            confidence=0.8,  # Could be calculated based on retrieval scores
            processing_time=processing_time,
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "RAG API Server",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "query": "/api/query (POST)",
        },
    }

if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    logger.info("Starting RAG API server on http://localhost:8000")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
