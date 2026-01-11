# RAG LLM Application - DVC Pipeline Architecture

## Pipeline Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DVC PIPELINE EXECUTION FLOW                          │
└─────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────┐
    │  Stage 1: install_dependencies       │
    │  ┌────────────────────────────────┐  │
    │  │ Install Python packages        │  │
    │  │ from requirements.txt          │  │
    │  └────────────────────────────────┘  │
    └────────────────┬─────────────────────┘
                     │
                     ▼
    ┌──────────────────────────────────────┐
    │  Stage 2: ingest_documents           │
    │  ┌────────────────────────────────┐  │
    │  │ • Load PDF files               │  │
    │  │ • Clean & chunk text           │  │
    │  │ • Generate embeddings          │  │
    │  │ • Store in Supabase            │  │
    │  └────────────────────────────────┘  │
    └────────────────┬─────────────────────┘
                     │
                     ▼
    ┌──────────────────────────────────────┐
    │  Stage 3: process_documents_local    │
    │  ┌────────────────────────────────┐  │
    │  │ • Load documents locally       │  │
    │  │ • Create chunks                │  │
    │  │ • Generate embeddings          │  │
    │  │ • Save to CSV                  │  │
    │  └────────────────────────────────┘  │
    └────────────────┬─────────────────────┘
                     │
            ┌────────┴────────┐
            │                 │
            ▼                 ▼
    ┌───────────────┐  ┌──────────────┐
    │ Stage 4:      │  │ Stage 5:     │
    │ test_         │  │ demo_        │
    │ retrieval     │  │ retrieval    │
    │               │  │              │
    │ • Load chunks │  │ • Predefined │
    │ • Test queries│  │   queries    │
    │ • Validate    │  │ • Show       │
    │   results     │  │   results    │
    └───────┬───────┘  └──────┬───────┘
            │                 │
            └────────┬────────┘
                     │
                     ▼
    ┌──────────────────────────────────────┐
    │  Stage 6: evaluate_pipeline          │
    │  ┌────────────────────────────────┐  │
    │  │ • Run test queries             │  │
    │  │ • Measure performance          │  │
    │  │ • Generate metrics             │  │
    │  └────────────────────────────────┘  │
    └────────────────┬─────────────────────┘
                     │
                     ▼
    ┌──────────────────────────────────────┐
    │  Stage 7: generate_docs              │
    │  ┌────────────────────────────────┐  │
    │  │ • Create pipeline report       │  │
    │  │ • Summarize results            │  │
    │  │ • Document metrics             │  │
    │  └────────────────────────────────┘  │
    └──────────────────────────────────────┘
```

## Data Flow

```
INPUT                    PROCESSING                    OUTPUT
─────                    ──────────                    ──────

PDF Files
   │
   ├─► ingest.py ───────► Supabase ──────┐
   │                                      │
   └─► PDFLoader ───┐                     │
                    │                     │
                    ▼                     │
              TextChunker                 │
                    │                     │
                    ▼                     │
            OpenAIEmbedder ───────────────┤
                    │                     │
                    ▼                     ▼
         text_chunks_and_         Vector Database
         embeddings_df.csv              │
                    │                     │
                    └──────┬──────────────┘
                           │
                           ▼
                    LocalRetriever
                           │
                    ┌──────┴──────┐
                    │             │
                    ▼             ▼
              Test Results   Demo Results
                    │             │
                    └──────┬──────┘
                           │
                           ▼
                  Pipeline Metrics
                           │
                           ▼
                  Final Report
```

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        RAG LLM Application                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Ingestion   │  │  Embeddings  │  │   Retrieval  │         │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤         │
│  │ • PDFLoader  │  │ • OpenAI     │  │ • Supabase   │         │
│  │ • Chunker    │  │ • Local      │  │ • Local      │         │
│  │              │  │   (sentence- │  │   (CSV-based)│         │
│  │              │  │   transform) │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Vector DB   │  │     LLM      │  │   Pipeline   │         │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤         │
│  │ • Supabase   │  │ • OpenAI     │  │ • RAG        │         │
│  │ • Local CSV  │  │ • Local      │  │   Pipeline   │         │
│  │              │  │   (Gemma,    │  │ • Query      │         │
│  │              │  │   Mistral)   │  │   Handler    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                      Configuration Layer                        │
├─────────────────────────────────────────────────────────────────┤
│  • settings.py (Environment config)                             │
│  • params.yaml (Pipeline parameters)                            │
│  • .env (Secrets and API keys)                                 │
└─────────────────────────────────────────────────────────────────┘
```

## File Dependencies

```
dvc.yaml
   │
   ├─► params.yaml (parameters)
   │
   ├─► .env (environment variables)
   │
   └─► Dependencies:
       │
       ├─► ingest.py
       │   └─► PDF files
       │
       ├─► rag_llm_app/
       │   ├─► app/main.py
       │   ├─► app/ingestion/
       │   ├─► app/embeddings/
       │   ├─► app/retriever/
       │   ├─► app/pipeline/
       │   └─► app/config/settings.py
       │
       └─► Outputs:
           ├─► data/documents/*.csv
           └─► outputs/*.{txt,json,md}
```

## Execution Modes

```
┌─────────────────────────────────────────────────────────────┐
│                    Execution Options                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Complete Pipeline                                       │
│     Command: dvc repro                                      │
│     Runs: All 7 stages sequentially                         │
│                                                             │
│  2. Specific Stage                                          │
│     Command: dvc repro <stage_name>                         │
│     Runs: Single stage + dependencies                       │
│                                                             │
│  3. Interactive Setup                                       │
│     Command: python setup_dvc.py                            │
│     Runs: Guided setup + selected stages                    │
│                                                             │
│  4. Windows Batch                                           │
│     Command: run_dvc.bat <command>                          │
│     Runs: Simplified Windows interface                      │
│                                                             │
│  5. Makefile (Unix/Linux/Mac)                              │
│     Command: make <target>                                  │
│     Runs: Simplified Unix interface                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Output Artifacts

```
outputs/
├── retrieval_test_results.txt
│   Purpose: Validation of retrieval accuracy
│   Format: Plain text
│   Generated by: test_retrieval stage
│
├── demo_results.txt
│   Purpose: Sample query demonstrations
│   Format: Plain text with examples
│   Generated by: demo_retrieval stage
│
├── pipeline_metrics.json
│   Purpose: Performance measurements
│   Format: JSON with timing/accuracy metrics
│   Generated by: evaluate_pipeline stage
│   Schema: {queries: [], avg_time: float}
│
├── retrieval_metrics.json
│   Purpose: Retrieval-specific metrics
│   Format: JSON
│   Generated by: demo_retrieval stage
│
└── PIPELINE_REPORT.md
    Purpose: Comprehensive execution report
    Format: Markdown documentation
    Generated by: generate_docs stage
```

## Configuration Hierarchy

```
Priority (High to Low):
  1. CLI Parameters (-P flag)
  2. params.yaml
  3. .env file
  4. settings.py defaults

Example:
  dvc repro -P chunking.max_tokens=1500
       ↓
  Overrides params.yaml value
       ↓
  Which overrides .env value
       ↓
  Which overrides settings.py default
```

## DVC Features Used

```
┌─────────────────────────────────────────────────────────┐
│ Feature              │ Usage in This Project            │
├──────────────────────┼──────────────────────────────────┤
│ Pipelines            │ Multi-stage RAG workflow         │
│ Dependencies         │ Track file/code changes          │
│ Parameters           │ Configurable settings            │
│ Metrics              │ Performance tracking             │
│ Outputs              │ Generated artifacts              │
│ Artifacts            │ Embeddings, models, reports      │
│ Experiments          │ Parameter tuning (future)        │
└─────────────────────────────────────────────────────────┘
```

---

**Legend:**

- `┌─┐ └─┘` : Component boundaries
- `│ ─ ├ ┤ ┬ ┴ ┼` : Connections
- `►` : Data flow direction
- `•` : List items
