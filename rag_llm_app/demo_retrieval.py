"""Demonstration of RAG retrieval with sample queries"""

import ast
import json
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


def demo_queries():
    """Run demo queries and write results/metrics for DVC."""
    csv_path = "data/documents/text_chunks_and_embeddings_df.csv"
    
    logger.info("Loading embeddings...")
    df = pd.read_csv(csv_path)
    df["embedding"] = df["embedding"].apply(lambda x: np.array(ast.literal_eval(x), dtype=np.float32))
    chunks = df.to_dict(orient="records")
    embeddings_tensor = torch.tensor(np.array(df["embedding"].tolist()), dtype=torch.float32)
    logger.info(f"Loaded {len(chunks)} chunks")
    
    retriever = LocalRetriever(embeddings=embeddings_tensor, chunks=chunks)
    embedder = LocalEmbedder()
    
    questions = [
        "What are the health benefits of protein?",
        "What nutrients should a healthy diet contain?",
        "How much water should people drink daily?",
        "What are carbohydrates and their role in nutrition?",
    ]
    
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    results_txt = output_dir / "demo_results.txt"
    metrics_json = output_dir / "retrieval_metrics.json"
    lines = []
    metrics = []
    
    lines.append("RAG RETRIEVAL DEMO (Human Nutrition Document)")
    lines.append(f"Documents loaded: {len(chunks)}")
    lines.append(f"Embedding model: {settings.LOCAL_EMBEDDING_MODEL}")
    lines.append("")
    
    for i, question in enumerate(questions, 1):
        lines.append(f"QUERY {i}: {question}")
        try:
            query_embedding = embedder.embed_text(question)
            documents = retriever.search(query_embedding, top_k=3, print_time=False)
            for j, doc in enumerate(documents, 1):
                snippet = doc['sentence_chunk'][:280].replace("\n", " ")
                lines.append(f"  [{j}] Page {doc['page_number']} (Similarity: {doc['similarity']:.4f}) {snippet}...")
            metrics.append({
                "question": question,
                "top_hits": [
                    {
                        "page": doc['page_number'],
                        "similarity": doc['similarity'],
                        "id": doc.get('id')
                    }
                    for doc in documents
                ]
            })
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            lines.append(f"❌ Error: {e}")
    
    results_txt.write_text("\n".join(lines), encoding="utf-8")
    metrics_json.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    logger.info(f"Wrote demo results to {results_txt}")
    logger.info(f"Wrote retrieval metrics to {metrics_json}")


if __name__ == "__main__":
    demo_queries()
