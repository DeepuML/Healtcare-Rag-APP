"""
Helper scripts for DVC pipeline stages
These scripts are called by dvc.yaml to avoid complex inline Python
"""
import json
import time
import sys
import os
from pathlib import Path
from datetime import datetime


def evaluate_pipeline():
    """Stage 6: Evaluate RAG Pipeline Performance"""
    # Force local backend for evaluation to avoid external quotas
    os.environ["MODEL_BACKEND"] = "local"
    os.environ["RETRIEVER_MODE"] = "local"
    os.environ.setdefault("LOCAL_LLM_MODEL", "sshleifer/tiny-gpt2")
    os.environ["USE_QUANTIZATION"] = "False"
    sys.path.insert(0, str(Path(__file__).parent / "rag_llm_app"))
    
    from app.config import settings
    from app.pipeline import RAGPipeline
    settings.MODEL_BACKEND = "local"
    settings.RETRIEVER_MODE = "local"
    settings.LOCAL_LLM_MODEL = os.environ.get("LOCAL_LLM_MODEL", "sshleifer/tiny-gpt2")
    settings.USE_QUANTIZATION = False
    
    pipeline = RAGPipeline(retriever_mode="local")
    test_queries = [
        'What are the health benefits of protein?',
        'What nutrients should a healthy diet contain?',
        'How much water should people drink daily?',
    ]
    
    results = []
    for q in test_queries:
        start = time.time()
        query_emb = pipeline.embedder.embed_text(q)
        docs = pipeline.retriever.search(query_emb)
        elapsed = time.time() - start
        results.append({
            'query': q,
            'time': elapsed,
            'num_docs': len(docs)
        })
    
    output_dir = Path('rag_llm_app/outputs')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / 'pipeline_metrics.json', 'w', encoding='utf-8') as f:
        json.dump({
            'queries': results,
            'avg_time': sum(r['time'] for r in results) / len(results)
        }, f, indent=2)
    
    print(f"Evaluated {len(results)} queries")
    print(f"Average response time: {sum(r['time'] for r in results) / len(results):.2f}s")


def generate_docs():
    """Stage 7: Generate Documentation"""
    sys.path.insert(0, str(Path(__file__).parent / "rag_llm_app"))
    
    from app.config import settings
    
    readme = f"""# RAG LLM Application - Pipeline Results

## Pipeline Execution Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Stages Completed
1. ✅ Dependencies Installation
2. ✅ Document Ingestion
3. ✅ Local Document Processing
4. ✅ Retrieval System Testing
5. ✅ Demo Queries Execution
6. ✅ Pipeline Performance Evaluation
7. ✅ Documentation Generation

## Output Files
- `data/documents/text_chunks_and_embeddings_df.csv`: Processed document chunks and embeddings
- `outputs/retrieval_test_results.txt`: Retrieval system test results
- `outputs/demo_results.txt`: Demo query results
- `outputs/pipeline_metrics.json`: Performance metrics
- `outputs/PIPELINE_REPORT.md`: This report

## Next Steps
- Run interactive queries: `python -m app.main query`
- View metrics: `cat outputs/pipeline_metrics.json`
- Customize settings in `.env` file

## Configuration
- Embedding Model: {settings.LOCAL_EMBEDDING_MODEL}
- Backend: {settings.MODEL_BACKEND}
"""
    
    output_dir = Path('outputs')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    (output_dir / 'PIPELINE_REPORT.md').write_text(readme, encoding='utf-8')
    print('Documentation generated successfully')


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pipeline_helpers.py <command>")
        print("Commands: evaluate_pipeline, generate_docs")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "evaluate_pipeline":
        evaluate_pipeline()
    elif command == "generate_docs":
        generate_docs()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
