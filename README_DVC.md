# DVC Pipeline for RAG LLM Application

This document explains how to use DVC (Data Version Control) to manage and run the RAG (Retrieval-Augmented Generation) pipeline.

## 📋 Prerequisites

1. Install DVC:

```bash
pip install dvc
```

2. Initialize DVC in the project (if not already done):

```bash
dvc init
```

3. Set up your environment variables in `.env` file:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
OPENAI_API_KEY=your_openai_api_key
MODEL_BACKEND=local  # or "api"
LOCAL_EMBEDDING_MODEL=all-mpnet-base-v2
EMBEDDING_DEVICE=cuda  # or "cpu"
```

## 🚀 Running the Pipeline

### Run Complete Pipeline

Execute all stages in sequence:

```bash
dvc repro
```

### Run Specific Stage

Execute a single stage:

```bash
# Install dependencies
dvc repro install_dependencies

# Ingest documents to Supabase
dvc repro ingest_documents

# Process documents locally
dvc repro process_documents_local

# Test retrieval system
dvc repro test_retrieval

# Run demo queries
dvc repro demo_retrieval

# Evaluate pipeline
dvc repro evaluate_pipeline

# Generate documentation
dvc repro generate_docs
```

### Run with Custom Parameters

Override parameters using `-P` flag:

```bash
dvc repro -P chunking.sentences_per_chunk=25
dvc repro -P embedding.model=text-embedding-3-large
```

## 📊 Pipeline Stages

| Stage                     | Description               | Outputs                      |
| ------------------------- | ------------------------- | ---------------------------- |
| `install_dependencies`    | Install Python packages   | Virtual environment packages |
| `ingest_documents`        | Process PDFs to Supabase  | Ingestion logs               |
| `process_documents_local` | Local document processing | CSV with chunks & embeddings |
| `test_retrieval`          | Test retrieval system     | Test results                 |
| `demo_retrieval`          | Run demo queries          | Demo results report          |
| `evaluate_pipeline`       | Performance evaluation    | Metrics JSON                 |
| `generate_docs`           | Create documentation      | Pipeline report              |

## 📈 Viewing Metrics and Outputs

### Check Pipeline Status

```bash
dvc status
```

### View Pipeline DAG

```bash
dvc dag
```

### Show Metrics

```bash
dvc metrics show
```

### Compare Runs

```bash
dvc metrics diff
```

### View Outputs

```bash
# Retrieval test results
cat outputs/retrieval_test_results.txt

# Demo results
cat outputs/demo_results.txt

# Performance metrics
cat outputs/pipeline_metrics.json

# Pipeline report
cat outputs/PIPELINE_REPORT.md
```

## 🔧 Configuration

### Edit Parameters

Modify `params.yaml` to change pipeline behavior:

```yaml
chunking:
  sentences_per_chunk: 20
  max_tokens: 1300

embedding:
  model: "text-embedding-3-small"
  batch_size: 100
```

### Modify Pipeline

Edit `dvc.yaml` to:

- Add new stages
- Change dependencies
- Update commands
- Modify outputs

## 📁 Output Files

After running the pipeline, you'll find:

```
outputs/
├── retrieval_test_results.txt    # Retrieval system test output
├── demo_results.txt               # Demo query results
├── pipeline_metrics.json          # Performance metrics
└── PIPELINE_REPORT.md             # Comprehensive report

rag_llm_app/data/documents/
└── text_chunks_and_embeddings_df.csv  # Processed chunks
```

## 🔄 Workflow Examples

### Complete Fresh Run

```bash
# Clean all outputs
dvc remove *.dvc -f

# Run entire pipeline
dvc repro

# View results
cat outputs/PIPELINE_REPORT.md
```

### Update Only Retrieval

```bash
# If you modified retrieval code
dvc repro test_retrieval demo_retrieval
```

### Experiment with Different Parameters

```bash
# Try different chunk sizes
dvc repro -P chunking.sentences_per_chunk=15

# Compare with baseline
dvc metrics diff
```

## 🐛 Troubleshooting

### Pipeline Fails

```bash
# Check which stage failed
dvc status

# Run stage with verbose output
dvc repro -v stage_name
```

### Reset Pipeline

```bash
# Remove all DVC-tracked outputs
dvc remove *.dvc -f

# Start fresh
dvc repro
```

### Check Dependencies

```bash
# Verify all inputs exist
dvc status

# View dependency graph
dvc dag
```

## 📚 Additional Resources

- [DVC Documentation](https://dvc.org/doc)
- [DVC Pipeline Guide](https://dvc.org/doc/user-guide/pipelines)
- [Experiment Tracking](https://dvc.org/doc/user-guide/experiment-management)

## 🎯 Next Steps

1. **Run the pipeline**: `dvc repro`
2. **Check outputs**: Review generated files in `outputs/`
3. **View metrics**: `dvc metrics show`
4. **Interactive queries**: `python -m app.main query` (from rag_llm_app/)
5. **Experiment**: Modify `params.yaml` and rerun

---

**Note**: Make sure you have the required PDF file (`human-nutrition-text.pdf`) in the project root before running document ingestion stages.
