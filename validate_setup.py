#!/usr/bin/env python
"""
Validate DVC Pipeline Setup
Checks if all required files and configurations are in place
"""
import os
import sys
from pathlib import Path
from typing import List, Tuple

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def check_file(filepath: str, required: bool = True) -> bool:
    """Check if a file exists"""
    exists = Path(filepath).exists()
    status = f"{Colors.GREEN}✅" if exists else f"{Colors.RED}❌"
    req_text = "REQUIRED" if required else "OPTIONAL"
    
    print(f"{status} {filepath:<50} [{req_text}]{Colors.END}")
    
    if required and not exists:
        return False
    return True

def check_directory(dirpath: str, required: bool = True) -> bool:
    """Check if a directory exists"""
    exists = Path(dirpath).is_dir()
    status = f"{Colors.GREEN}✅" if exists else f"{Colors.RED}❌"
    req_text = "REQUIRED" if required else "OPTIONAL"
    
    print(f"{status} {dirpath:<50} [{req_text}]{Colors.END}")
    
    if required and not exists:
        return False
    return True

def check_env_var(var_name: str, required: bool = True) -> bool:
    """Check if an environment variable is set"""
    value = os.getenv(var_name)
    exists = value is not None and value.strip() != ""
    status = f"{Colors.GREEN}✅" if exists else f"{Colors.RED}❌"
    req_text = "REQUIRED" if required else "OPTIONAL"
    
    print(f"{status} {var_name:<50} [{req_text}]{Colors.END}")
    
    if required and not exists:
        return False
    return True

def check_python_package(package_name: str, required: bool = True) -> bool:
    """Check if a Python package is installed"""
    try:
        __import__(package_name)
        exists = True
    except ImportError:
        exists = False
    
    status = f"{Colors.GREEN}✅" if exists else f"{Colors.RED}❌"
    req_text = "REQUIRED" if required else "OPTIONAL"
    
    print(f"{status} {package_name:<50} [{req_text}]{Colors.END}")
    
    if required and not exists:
        return False
    return True

def validate_pipeline() -> Tuple[int, int, List[str]]:
    """
    Validate the DVC pipeline setup
    Returns: (passed_checks, total_checks, warnings)
    """
    passed = 0
    total = 0
    warnings = []
    
    # Check DVC files
    print_header("1. DVC Configuration Files")
    checks = [
        ("dvc.yaml", True),
        ("params.yaml", True),
        (".dvcignore", True),
        (".dvc", True),  # DVC directory
    ]
    
    for filepath, required in checks:
        total += 1
        if check_file(filepath, required) or check_directory(filepath, required):
            passed += 1
    
    # Check helper scripts
    print_header("2. Helper Scripts")
    checks = [
        ("setup_dvc.py", True),
        ("run_dvc.bat", False),
        ("Makefile", False),
        ("README_DVC.md", True),
        ("QUICKSTART.md", True),
        ("PIPELINE_ARCHITECTURE.md", False),
    ]
    
    for filepath, required in checks:
        total += 1
        if check_file(filepath, required):
            passed += 1
    
    # Check application files
    print_header("3. Application Files")
    checks = [
        ("ingest.py", True),
        ("rag_llm_app/app/main.py", True),
        ("rag_llm_app/test_retrieval.py", True),
        ("rag_llm_app/demo_retrieval.py", True),
        ("rag_llm_app/requirements.txt", True),
        ("rag_llm_app/app/config/settings.py", True),
    ]
    
    for filepath, required in checks:
        total += 1
        if check_file(filepath, required):
            passed += 1
    
    # Check directories
    print_header("4. Required Directories")
    checks = [
        ("outputs", True),
        ("rag_llm_app/app", True),
        ("rag_llm_app/data", False),
        ("rag_llm_app/data/documents", False),
    ]
    
    for dirpath, required in checks:
        total += 1
        if check_directory(dirpath, required):
            passed += 1
    
    # Check Python packages
    print_header("5. Python Packages")
    
    # Try to load .env first
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        warnings.append("python-dotenv not installed - cannot load .env file")
    
    checks = [
        ("dvc", True),
        ("torch", False),
        ("pandas", False),
        ("openai", False),
        ("supabase", False),
    ]
    
    for package, required in checks:
        total += 1
        if check_python_package(package, required):
            passed += 1
    
    # Check environment variables
    print_header("6. Environment Variables (from .env)")
    
    if not Path(".env").exists():
        print(f"{Colors.YELLOW}⚠️  .env file not found. Create one for production use.{Colors.END}")
        warnings.append(".env file not found - using defaults")
        # Skip env var checks
    else:
        checks = [
            ("MODEL_BACKEND", False),
            ("LOCAL_EMBEDDING_MODEL", False),
            ("SUPABASE_URL", False),
            ("SUPABASE_SERVICE_ROLE_KEY", False),
            ("OPENAI_API_KEY", False),
        ]
        
        for var, required in checks:
            total += 1
            if check_env_var(var, required):
                passed += 1
    
    # Check optional data files
    print_header("7. Data Files (Optional)")
    checks = [
        ("human-nutrition-text.pdf", False),
        ("rag_llm_app/data/documents/text_chunks_and_embeddings_df.csv", False),
    ]
    
    for filepath, required in checks:
        total += 1
        if check_file(filepath, required):
            passed += 1
        else:
            if "pdf" in filepath:
                warnings.append("PDF file not found - needed for document ingestion")
            elif "csv" in filepath:
                warnings.append("Embeddings CSV not found - will be generated on first run")
    
    return passed, total, warnings

def main():
    """Main validation function"""
    print(f"""
{Colors.BOLD}╔══════════════════════════════════════════════════════════╗
║      DVC Pipeline Setup Validation                       ║
╚══════════════════════════════════════════════════════════╝{Colors.END}
    """)
    
    passed, total, warnings = validate_pipeline()
    
    # Summary
    print_header("Validation Summary")
    
    percentage = (passed / total * 100) if total > 0 else 0
    
    if percentage == 100:
        status_color = Colors.GREEN
        status_text = "EXCELLENT"
    elif percentage >= 80:
        status_color = Colors.GREEN
        status_text = "GOOD"
    elif percentage >= 60:
        status_color = Colors.YELLOW
        status_text = "ACCEPTABLE"
    else:
        status_color = Colors.RED
        status_text = "NEEDS ATTENTION"
    
    print(f"Checks Passed: {status_color}{passed}/{total} ({percentage:.1f}%){Colors.END}")
    print(f"Status: {status_color}{status_text}{Colors.END}")
    
    # Warnings
    if warnings:
        print(f"\n{Colors.YELLOW}⚠️  Warnings:{Colors.END}")
        for warning in warnings:
            print(f"   - {warning}")
    
    # Recommendations
    print(f"\n{Colors.BOLD}Recommendations:{Colors.END}")
    
    if not Path(".dvc").exists():
        print(f"  {Colors.RED}1. Initialize DVC: dvc init{Colors.END}")
    
    if not Path(".env").exists():
        print(f"  {Colors.YELLOW}2. Create .env file: python setup_dvc.py{Colors.END}")
    
    if not any(Path(p).exists() for p in ["human-nutrition-text.pdf"]):
        print(f"  {Colors.YELLOW}3. Add PDF files for document ingestion{Colors.END}")
    
    try:
        __import__("dvc")
        print(f"  {Colors.GREEN}4. Ready to run: dvc repro{Colors.END}")
    except ImportError:
        print(f"  {Colors.RED}4. Install DVC: pip install dvc{Colors.END}")
    
    # Next steps
    print(f"\n{Colors.BOLD}Next Steps:{Colors.END}")
    print("  1. Fix any failing checks marked with ❌")
    print("  2. Review warnings marked with ⚠️")
    print("  3. Run: python setup_dvc.py (for interactive setup)")
    print("  4. Or run: dvc repro (to execute pipeline)")
    print("\nFor detailed documentation, see README_DVC.md")
    
    # Exit code
    if percentage >= 80:
        print(f"\n{Colors.GREEN}✅ Setup validation passed!{Colors.END}\n")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}❌ Please fix the issues above before running the pipeline.{Colors.END}\n")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Validation interrupted by user{Colors.END}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Error during validation: {e}{Colors.END}")
        sys.exit(1)
