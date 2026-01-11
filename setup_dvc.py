#!/usr/bin/env python
"""
Quick start script to initialize and run the DVC pipeline
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and print status"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}\n")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if result.returncode != 0:
        print(f"❌ Failed: {description}")
        return False
    else:
        print(f"✅ Success: {description}")
        return True
    
def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║         RAG LLM Application - DVC Pipeline Setup        ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Check if DVC is installed
    print("Checking DVC installation...")
    result = subprocess.run("dvc version", shell=True, capture_output=True)
    if result.returncode != 0:
        print("❌ DVC is not installed. Installing...")
        if not run_command("pip install dvc", "Installing DVC"):
            sys.exit(1)
    else:
        print("✅ DVC is already installed")
    
    # Initialize DVC if not already done
    dvc_dir = Path(".dvc")
    if not dvc_dir.exists():
        print("\nInitializing DVC repository...")
        if not run_command("dvc init", "Initializing DVC"):
            sys.exit(1)
    else:
        print("✅ DVC is already initialized")
    
    # Check for .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("\n⚠️  Warning: .env file not found")
        print("Please create a .env file with your configuration:")
        print("""
Example .env:
--------------
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
OPENAI_API_KEY=your_openai_api_key
MODEL_BACKEND=local
LOCAL_EMBEDDING_MODEL=all-mpnet-base-v2
EMBEDDING_DEVICE=cuda
        """)
        
        create_env = input("\nDo you want to create a template .env file? (y/n): ")
        if create_env.lower() == 'y':
            with open('.env', 'w') as f:
                f.write("""# Environment Configuration for RAG LLM Application

# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# OpenAI API (if using API backend)
OPENAI_API_KEY=your_openai_api_key_here

# Model Backend Selection
MODEL_BACKEND=local  # Options: "local" or "api"

# Local Embedding Configuration
LOCAL_EMBEDDING_MODEL=all-mpnet-base-v2
LOCAL_EMBEDDING_DIMENSION=768
EMBEDDING_DEVICE=cuda  # Options: "cuda" or "cpu"

# Local LLM Configuration
LOCAL_LLM_MODEL=google/gemma-7b-it
USE_QUANTIZATION=False
LLM_DEVICE=cuda
ATTENTION_IMPLEMENTATION=sdpa

# API Configuration (OpenAI)
API_EMBEDDING_MODEL=text-embedding-3-small
API_EMBEDDING_DIMENSION=1536
API_LLM_MODEL=gpt-4-turbo-preview

# Generation Parameters
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=512

# Chunking Configuration
CHUNK_SIZE=10
MIN_TOKEN_LENGTH=30
PAGE_NUMBER_OFFSET=0
""")
            print("✅ Created template .env file. Please edit it with your actual values.")
    
    # Create necessary directories
    print("\nCreating output directories...")
    Path("outputs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    print("✅ Directories created")
    
    # Ask user what to do
    print("\n" + "="*60)
    print("What would you like to do?")
    print("="*60)
    print("1. Install dependencies only")
    print("2. Run complete pipeline (all stages)")
    print("3. Run specific stage")
    print("4. View pipeline DAG")
    print("5. Check pipeline status")
    print("6. Exit")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    if choice == '1':
        run_command("dvc repro install_dependencies", "Installing dependencies")
    
    elif choice == '2':
        print("\n⚠️  This will run the entire pipeline. Make sure you have:")
        print("   - Configured your .env file")
        print("   - PDF file available (if running ingestion)")
        confirm = input("\nContinue? (y/n): ")
        if confirm.lower() == 'y':
            run_command("dvc repro", "Running complete pipeline")
            print("\n" + "="*60)
            print("📊 View results:")
            print("   - Pipeline report: outputs/PIPELINE_REPORT.md")
            print("   - Metrics: dvc metrics show")
            print("   - Status: dvc status")
    
    elif choice == '3':
        print("\nAvailable stages:")
        print("  - install_dependencies")
        print("  - ingest_documents")
        print("  - process_documents_local")
        print("  - test_retrieval")
        print("  - demo_retrieval")
        print("  - evaluate_pipeline")
        print("  - generate_docs")
        stage = input("\nEnter stage name: ").strip()
        run_command(f"dvc repro {stage}", f"Running stage: {stage}")
    
    elif choice == '4':
        run_command("dvc dag", "Displaying pipeline DAG")
    
    elif choice == '5':
        run_command("dvc status", "Checking pipeline status")
    
    elif choice == '6':
        print("\n👋 Goodbye!")
        sys.exit(0)
    
    else:
        print("❌ Invalid choice")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ Setup complete!")
    print("="*60)
    print("\nNext steps:")
    print("  - Run pipeline: dvc repro")
    print("  - View metrics: dvc metrics show")
    print("  - Read documentation: README_DVC.md")
    print("  - Interactive queries: cd rag_llm_app && python -m app.main query")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
