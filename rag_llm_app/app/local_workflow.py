"""Local-only RAG workflow (matches notebook implementation)"""

import sys
import torch
import pandas as pd
import numpy as np
import ast
from pathlib import Path
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.ingestion import PDFLoader, TextChunker
from app.embeddings import LocalEmbedder
from app.retriever import LocalRetriever
from app.llm import LocalLLMGenerator
from app.utils import get_logger

logger = get_logger(__name__)


def create_local_embeddings(pdf_path: str | Path, save_csv: bool = True):
    """
    Create embeddings from PDF using local models (matching notebook workflow)
    
    Args:
        pdf_path: Path to PDF file
        save_csv: Whether to save embeddings to CSV
        
    Returns:
        Tuple of (embeddings_tensor, chunks_list)
    """
    logger.info("=" * 80)
    logger.info("CREATING LOCAL EMBEDDINGS (NOTEBOOK WORKFLOW)")
    logger.info("=" * 80)
    
    # 1. Load PDF
    loader = PDFLoader()
    pages_and_texts = loader.load_pdf(pdf_path)
    logger.info(f"Loaded {len(pages_and_texts)} pages")
    
    # 2. Chunk text
    chunker = TextChunker()
    chunks = chunker.create_chunks(pages_and_texts)
    logger.info(f"Created {len(chunks)} chunks")
    
    # 3. Create embeddings with local model
    embedder = LocalEmbedder()
    chunk_texts = [chunk["sentence_chunk"] for chunk in chunks]
    embeddings_list = embedder.embed_chunks(chunk_texts, batch_size=32)
    
    # 4. Add embeddings to chunks
    for chunk, embedding in zip(chunks, embeddings_list):
        chunk["embedding"] = embedding
    
    # 5. Save to CSV if requested
    if save_csv:
        df = pd.DataFrame(chunks)
        csv_path = Path(pdf_path).parent / "text_chunks_and_embeddings_df.csv"
        df.to_csv(csv_path, index=False)
        logger.info(f"Saved embeddings to {csv_path}")
    
    # 6. Convert to torch tensor
    embeddings_tensor = torch.tensor(
        np.array(embeddings_list),
        dtype=torch.float32
    )
    
    logger.info("=" * 80)
    logger.info("LOCAL EMBEDDING CREATION COMPLETE")
    logger.info("=" * 80)
    
    return embeddings_tensor, chunks


def load_local_embeddings(csv_path: str | Path):
    """
    Load embeddings from CSV (matching notebook workflow)
    
    Args:
        csv_path: Path to embeddings CSV
        
    Returns:
        Tuple of (embeddings_tensor, chunks_list)
    """
    logger.info(f"Loading embeddings from {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    # Convert embedding column back to arrays using ast.literal_eval
    df["embedding"] = df["embedding"].apply(lambda x: np.array(ast.literal_eval(x), dtype=np.float32))
    
    # Convert to list of dicts
    chunks = df.to_dict(orient="records")
    
    # Convert to torch tensor
    embeddings_tensor = torch.tensor(
        np.array(df["embedding"].tolist()),
        dtype=torch.float32
    )
    
    logger.info(f"Loaded {len(chunks)} chunks with embeddings")
    
    return embeddings_tensor, chunks


def interactive_query_local(embeddings: torch.Tensor, chunks: list):
    """
    Run interactive query loop with local models (matching notebook workflow)
    
    Args:
        embeddings: Tensor of embeddings
        chunks: List of chunk dictionaries
    """
    logger.info("=" * 80)
    logger.info("STARTING LOCAL RAG QUERY (NOTEBOOK WORKFLOW)")
    logger.info("=" * 80)
    
    # Initialize components
    embedder = LocalEmbedder()
    retriever = LocalRetriever(embeddings=embeddings, chunks=chunks)
    generator = LocalLLMGenerator()
    
    print("\n🤖 Local RAG Assistant Ready!")
    print(f"Using: {settings.LOCAL_EMBEDDING_MODEL} + {settings.LOCAL_LLM_MODEL}")
    print("Ask questions about your documents (type 'exit' to quit)\n")
    
    while True:
        try:
            question = input("Question: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            # Embed query
            query_embedding = embedder.embed_text(question)
            
            # Retrieve relevant documents
            documents = retriever.search(query_embedding, print_time=True)
            
            # Format context
            context = retriever.format_context(documents)
            
            # Generate answer
            answer = generator.generate(query=question, context=context)
            
            print(f"\n📝 Answer:\n{answer}\n")
            
            # Show sources
            print("📚 Sources:")
            for i, doc in enumerate(documents, 1):
                print(f"  [{i}] Page {doc['page_number']} (similarity: {doc['similarity']:.3f})")
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            print(f"❌ Error: {e}\n")


def main():
    """Main entry point for local workflow"""
    if len(sys.argv) < 2:
        print("Local RAG Workflow (Notebook Implementation)")
        print("\nUsage:")
        print("  Create embeddings: python -m app.local_workflow create <pdf_path>")
        print("  Load & query:      python -m app.local_workflow query <embeddings_csv>")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "create":
        if len(sys.argv) < 3:
            print("Error: Please provide PDF path")
            print("Usage: python -m app.local_workflow create <pdf_path>")
            sys.exit(1)
        
        pdf_path = sys.argv[2]
        embeddings, chunks = create_local_embeddings(pdf_path)
        
        print("\n✅ Embeddings created successfully!")
        print(f"   Embeddings shape: {embeddings.shape}")
        print(f"   Number of chunks: {len(chunks)}")
        print("\nTo query, run:")
        print(f"python -m app.local_workflow query {Path(pdf_path).parent}/text_chunks_and_embeddings_df.csv")
        
    elif command == "query":
        if len(sys.argv) < 3:
            print("Error: Please provide embeddings CSV path")
            print("Usage: python -m app.local_workflow query <embeddings_csv>")
            sys.exit(1)
        
        csv_path = sys.argv[2]
        embeddings, chunks = load_local_embeddings(csv_path)
        interactive_query_local(embeddings, chunks)
        
    else:
        print(f"Unknown command: {command}")
        print("Available commands: create, query")
        sys.exit(1)


if __name__ == "__main__":
    main()
