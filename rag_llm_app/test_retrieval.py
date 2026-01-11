"""Retrieval smoke test (interactive optional)"""

import argparse
import ast
from pathlib import Path
import sys
import torch
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.embeddings import LocalEmbedder
from app.retriever import LocalRetriever
from app.utils import get_logger

logger = get_logger(__name__)


def load_embeddings(csv_path: str):
    df = pd.read_csv(csv_path)
    df["embedding"] = df["embedding"].apply(lambda x: np.array(ast.literal_eval(x), dtype=np.float32))
    chunks = df.to_dict(orient="records")
    embeddings_tensor = torch.tensor(np.array(df["embedding"].tolist()), dtype=torch.float32)
    return embeddings_tensor, chunks


def run_batch(questions, retriever, embedder, out_path: Path):
    """Run a fixed set of questions and write a brief report."""
    out_path.parent.mkdir(exist_ok=True, parents=True)
    lines = []
    for q in questions:
        logger.info(f"Processing question: {q}")
        query_embedding = embedder.embed_text(q)
        documents = retriever.search(query_embedding, print_time=False)
        lines.append(f"Question: {q}")
        for i, doc in enumerate(documents, 1):
            snippet = doc['sentence_chunk'][:180].replace("\n", " ")
            lines.append(f"  [{i}] Page {doc['page_number']} (sim={doc['similarity']:.4f}) {snippet}...")
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"Wrote retrieval test results to {out_path}")


def run_interactive(retriever, embedder):
    print("\n🤖 RAG Retrieval System Ready!")
    print("(Query-only mode - No LLM generation)\n")
    while True:
        try:
            question = input("Question: ").strip()
            if not question:
                continue
            if question.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            query_embedding = embedder.embed_text(question)
            documents = retriever.search(query_embedding, print_time=True)
            print("\n📚 Retrieved Documents:")
            for i, doc in enumerate(documents, 1):
                print(f"\n[{i}] Page {doc['page_number']} (Similarity: {doc['similarity']:.4f})")
                print(f"    {doc['sentence_chunk'][:200]}...")
            print()
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            print(f"❌ Error: {e}\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--csv", default="data/documents/text_chunks_and_embeddings_df.csv", help="Embeddings CSV path")
    parser.add_argument("--output", default="outputs/retrieval_test_results.txt", help="Where to write batch results")
    args = parser.parse_args()

    logger.info("Loading embeddings...")
    embeddings_tensor, chunks = load_embeddings(args.csv)
    logger.info(f"Loaded {len(chunks)} chunks")

    retriever = LocalRetriever(embeddings=embeddings_tensor, chunks=chunks)
    embedder = LocalEmbedder()

    if args.interactive:
        run_interactive(retriever, embedder)
    else:
        default_questions = [
            "What are the health benefits of protein?",
            "What nutrients should a healthy diet contain?",
            "How much water should people drink daily?",
        ]
        run_batch(default_questions, retriever, embedder, Path(args.output))


if __name__ == "__main__":
    main()
