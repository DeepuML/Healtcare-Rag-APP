# 🚀 DVC Pipeline Quick Start Guide

## Overview

This project now includes a complete DVC (Data Version Control) pipeline that automates the entire RAG (Retrieval-Augmented Generation) workflow from data ingestion to evaluation.

## 📁 New Files Created

```
Prodution_RAG/
├── dvc.yaml                    # Main DVC pipeline configuration
├── params.yaml                 # Configurable parameters
├── .dvcignore                  # Files to ignore in DVC
├── setup_dvc.py               # Interactive setup script
├── run_dvc.bat                # Windows batch runner
├── Makefile                   # Unix/Linux make commands
├── README_DVC.md              # Detailed DVC documentation
└── outputs/                   # Generated outputs directory
```

## ⚡ Quick Start (3 steps)

### Step 1: Install DVC

```bash
pip install dvc
```

### Step 2: Initialize DVC

```bash
dvc init
```

### Step 3: Run the Pipeline

**Option A - Interactive Setup (Recommended):**

```bash
python setup_dvc.py
```

**Option B - Direct Execution:**

```bash
dvc repro
```

**Option C - Windows Batch File:**

```cmd
run_dvc.bat repro
```

## 🎯 Available Commands

### Windows (Batch File)

```cmd
run_dvc.bat help          # Show all commands
run_dvc.bat setup         # Interactive setup
run_dvc.bat repro         # Run full pipeline
run_dvc.bat status        # Check status
run_dvc.bat metrics       # View metrics
run_dvc.bat test          # Run tests only
run_dvc.bat demo          # Run demo queries
run_dvc.bat query         # Interactive Q&A
run_dvc.bat clean         # Clean outputs
run_dvc.bat report        # View report
```

### Unix/Linux/Mac (Makefile)

```bash
make help                 # Show all commands
make setup                # Interactive setup
make repro                # Run full pipeline
make status               # Check status
make metrics              # View metrics
make test                 # Run tests only
make demo                 # Run demo queries
make query                # Interactive Q&A
make clean                # Clean outputs
make report               # View report
```

### Direct DVC Commands

```bash
# Run complete pipeline
dvc repro

# Run specific stage
dvc repro test_retrieval

# Check what's changed
dvc status

# View pipeline graph
dvc dag

# Show metrics
dvc metrics show

# Compare experiments
dvc metrics diff
```

## 📊 Pipeline Stages

The pipeline includes 7 stages:

1. **install_dependencies** - Install Python packages
2. **ingest_documents** - Process PDFs to Supabase
3. **process_documents_local** - Local document processing
4. **test_retrieval** - Test retrieval system
5. **demo_retrieval** - Run demo queries
6. **evaluate_pipeline** - Performance evaluation
7. **generate_docs** - Create documentation

## 🔧 Configuration

### Environment Variables (.env)

Create a `.env` file in the project root:

```env
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# OpenAI (optional)
OPENAI_API_KEY=your_openai_api_key

# Model Backend
MODEL_BACKEND=local  # or "api"

# Local Models
LOCAL_EMBEDDING_MODEL=all-mpnet-base-v2
EMBEDDING_DEVICE=cuda  # or "cpu"
```

### Pipeline Parameters (params.yaml)

Customize pipeline behavior:

```yaml
chunking:
  sentences_per_chunk: 20
  max_tokens: 1300

embedding:
  model: "text-embedding-3-small"
  batch_size: 100

retrieval:
  top_k: 5
  similarity_threshold: 0.7
```

## 📈 Outputs Generated

After running the pipeline, you'll find:

```
outputs/
├── retrieval_test_results.txt     # Test results
├── demo_results.txt                # Demo output
├── pipeline_metrics.json           # Performance metrics
└── PIPELINE_REPORT.md              # Comprehensive report

rag_llm_app/data/documents/
└── text_chunks_and_embeddings_df.csv  # Processed data
```

## 🎓 Usage Examples

### Example 1: First Time Setup

```bash
# Windows
python setup_dvc.py

# Unix/Linux/Mac
make setup
```

### Example 2: Run Full Pipeline

```bash
# Windows
run_dvc.bat repro

# Unix/Linux/Mac
make repro

# Direct DVC
dvc repro
```

### Example 3: Test Retrieval Only

```bash
# Windows
run_dvc.bat test

# Unix/Linux/Mac
make test

# Direct DVC
dvc repro test_retrieval
```

### Example 4: Experiment with Parameters

```bash
# Edit params.yaml, then:
dvc repro

# Or override inline:
dvc repro -P chunking.sentences_per_chunk=25
```

### Example 5: Interactive Queries

```bash
# Windows
run_dvc.bat query

# Unix/Linux/Mac
make query

# Direct command
cd rag_llm_app
python -m app.main query
```

## 🔍 Monitoring and Debugging

### Check Pipeline Status

```bash
dvc status
```

### View Dependency Graph

```bash
dvc dag
```

### See What Changed

```bash
dvc diff
```

### Debug Failed Stage

```bash
dvc repro -v stage_name
```

## 📚 Documentation

For detailed information, see:

- **[README_DVC.md](README_DVC.md)** - Complete DVC documentation
- **[dvc.yaml](dvc.yaml)** - Pipeline configuration
- **[params.yaml](params.yaml)** - Parameter configuration

## 🆘 Troubleshooting

### DVC Not Found

```bash
pip install dvc
```

### Pipeline Fails

```bash
# Check status
dvc status

# Run with verbose output
dvc repro -v

# Clean and retry
run_dvc.bat clean
dvc repro
```

### Missing Dependencies

```bash
# Windows
run_dvc.bat deps

# Unix/Linux/Mac
make deps

# Direct
pip install -r rag_llm_app/requirements.txt
```

### Missing .env File

```bash
# Run setup to create template
python setup_dvc.py
```

## 🎁 Benefits of Using DVC

1. **Reproducibility** - Run the same pipeline consistently
2. **Tracking** - Version control for data and models
3. **Automation** - No manual step execution
4. **Metrics** - Track performance over time
5. **Experiments** - Easy parameter comparison
6. **Documentation** - Self-documenting pipeline

## 🚦 Next Steps

1. ✅ **Setup**: Run `python setup_dvc.py`
2. ✅ **Configure**: Edit `.env` with your credentials
3. ✅ **Execute**: Run `dvc repro`
4. ✅ **Monitor**: Check `outputs/PIPELINE_REPORT.md`
5. ✅ **Experiment**: Modify `params.yaml` and rerun
6. ✅ **Query**: Run interactive mode with `run_dvc.bat query`

## 📞 Support

For issues or questions:

- Check [README_DVC.md](README_DVC.md) for detailed docs
- Review [DVC Documentation](https://dvc.org/doc)
- Examine pipeline logs in `outputs/`

---

**Happy experimenting! 🎉**
