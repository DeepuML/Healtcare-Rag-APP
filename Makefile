# Makefile for RAG LLM Application DVC Pipeline
# Usage: make [target]

.PHONY: help install init setup clean status dag repro metrics test demo query

# Default target
help:
	@echo "╔══════════════════════════════════════════════════════════╗"
	@echo "║         RAG LLM Application - DVC Pipeline              ║"
	@echo "╚══════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Available targets:"
	@echo "  make install       - Install DVC and dependencies"
	@echo "  make init          - Initialize DVC repository"
	@echo "  make setup         - Run interactive setup script"
	@echo "  make repro         - Run complete DVC pipeline"
	@echo "  make status        - Check pipeline status"
	@echo "  make dag           - Show pipeline DAG"
	@echo "  make metrics       - Display pipeline metrics"
	@echo "  make test          - Run retrieval tests only"
	@echo "  make demo          - Run demo queries only"
	@echo "  make query         - Start interactive query mode"
	@echo "  make clean         - Clean DVC outputs"
	@echo "  make report        - View pipeline report"
	@echo ""

# Install DVC
install:
	@echo "📦 Installing DVC..."
	pip install dvc
	@echo "✅ DVC installed"

# Initialize DVC
init:
	@echo "🔧 Initializing DVC..."
	dvc init
	@echo "✅ DVC initialized"

# Run setup script
setup:
	@echo "🚀 Running setup script..."
	python setup_dvc.py

# Run complete pipeline
repro:
	@echo "🏃 Running DVC pipeline..."
	dvc repro
	@echo "✅ Pipeline complete"
	@echo ""
	@echo "📊 View results:"
	@echo "   - Report: make report"
	@echo "   - Metrics: make metrics"

# Check pipeline status
status:
	@echo "📋 Checking pipeline status..."
	dvc status

# Show pipeline DAG
dag:
	@echo "📊 Pipeline DAG:"
	dvc dag

# Display metrics
metrics:
	@echo "📈 Pipeline Metrics:"
	dvc metrics show

# Run only retrieval tests
test:
	@echo "🧪 Running retrieval tests..."
	dvc repro test_retrieval
	@cat outputs/retrieval_test_results.txt

# Run demo queries
demo:
	@echo "🎯 Running demo queries..."
	dvc repro demo_retrieval
	@cat outputs/demo_results.txt

# Interactive query mode
query:
	@echo "💬 Starting interactive query mode..."
	cd rag_llm_app && python -m app.main query

# View pipeline report
report:
	@if [ -f outputs/PIPELINE_REPORT.md ]; then \
		cat outputs/PIPELINE_REPORT.md; \
	else \
		echo "❌ Report not generated yet. Run 'make repro' first."; \
	fi

# Clean outputs
clean:
	@echo "🧹 Cleaning DVC outputs..."
	rm -rf outputs/*
	rm -rf rag_llm_app/data/documents/*.csv
	dvc gc -w
	@echo "✅ Cleaned"

# Install project dependencies
deps:
	@echo "📦 Installing project dependencies..."
	pip install -r rag_llm_app/requirements.txt
	@echo "✅ Dependencies installed"

# Run specific stage
stage:
	@echo "Available stages:"
	@echo "  - install_dependencies"
	@echo "  - ingest_documents"
	@echo "  - process_documents_local"
	@echo "  - test_retrieval"
	@echo "  - demo_retrieval"
	@echo "  - evaluate_pipeline"
	@echo "  - generate_docs"
	@read -p "Enter stage name: " stage; \
	dvc repro $$stage

# Quick start (install, init, and setup)
quickstart: install init setup
	@echo "✅ Quick start complete!"
	@echo "Run 'make repro' to execute the pipeline"
