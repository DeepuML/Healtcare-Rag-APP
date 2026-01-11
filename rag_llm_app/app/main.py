"""Main CLI entry point for RAG LLM Application"""

import sys
from pathlib import Path
from app.config import settings
from app.ingestion import PDFLoader, TextChunker
from app.embeddings import OpenAIEmbedder
from app.vectorstore import SupabaseVectorStore
from app.pipeline import RAGPipeline
from app.utils import get_logger

logger = get_logger(__name__)


def ingest_document(pdf_path: str | Path):
    """
    Ingest a PDF document into the vector store
    
    Args:
        pdf_path: Path to PDF file
    """
    logger.info("=" * 80)
    logger.info("STARTING DOCUMENT INGESTION")
    logger.info("=" * 80)
    
    # Validate settings
    settings.validate()
    
    # 1. Load PDF
    loader = PDFLoader()
    pages_and_texts = loader.load_pdf(pdf_path)
    
    # 2. Chunk text
    chunker = TextChunker()
    chunks = chunker.create_chunks(pages_and_texts)
    
    # 3. Create embeddings
    embedder = OpenAIEmbedder()
    chunk_texts = [chunk["sentence_chunk"] for chunk in chunks]
    embeddings = embedder.embed_chunks(chunk_texts)
    
    # 4. Store in vector database
    vector_store = SupabaseVectorStore()
    vector_store.insert_chunks(chunks, embeddings)
    
    logger.info("=" * 80)
    logger.info("DOCUMENT INGESTION COMPLETE")
    logger.info("=" * 80)


def interactive_query():
    """Run interactive query loop"""
    logger.info("=" * 80)
    logger.info("STARTING INTERACTIVE RAG QUERY")
    logger.info("=" * 80)
    
    # Validate settings
    settings.validate()
    
    # Initialize pipeline
    pipeline = RAGPipeline()
    
    print("\n🤖 RAG Assistant Ready!")
    print("Ask questions about your documents (type 'exit' to quit)\n")
    
    while True:
        try:
            question = input("Question: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            # Get answer
            result = pipeline.query(question, return_context=True)
            
            print(f"\n📝 Answer:\n{result['answer']}\n")
            
            # Show sources
            print("📚 Sources:")
            for i, doc in enumerate(result['context'], 1):
                print(f"  [{i}] Page {doc['page_number']} (similarity: {doc['similarity']:.3f})")
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            print(f"❌ Error: {e}\n")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Ingest document: python -m app.main ingest <pdf_path>")
        print("  Query mode:      python -m app.main query")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "ingest":
        if len(sys.argv) < 3:
            print("Error: Please provide PDF path")
            print("Usage: python -m app.main ingest <pdf_path>")
            sys.exit(1)
        
        pdf_path = sys.argv[2]
        ingest_document(pdf_path)
        
    elif command == "query":
        interactive_query()
        
    else:
        print(f"Unknown command: {command}")
        print("Available commands: ingest, query")
        sys.exit(1)


if __name__ == "__main__":
    main()
