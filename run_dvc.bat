@echo off
REM DVC Pipeline Runner for Windows
REM Usage: run_dvc.bat [command]

setlocal enabledelayedexpansion

if "%1"=="" goto :help
if "%1"=="help" goto :help
if "%1"=="install" goto :install
if "%1"=="init" goto :init
if "%1"=="setup" goto :setup
if "%1"=="repro" goto :repro
if "%1"=="status" goto :status
if "%1"=="dag" goto :dag
if "%1"=="metrics" goto :metrics
if "%1"=="test" goto :test
if "%1"=="demo" goto :demo
if "%1"=="query" goto :query
if "%1"=="clean" goto :clean
if "%1"=="report" goto :report
if "%1"=="deps" goto :deps
goto :help

:help
echo ╔══════════════════════════════════════════════════════════╗
echo ║         RAG LLM Application - DVC Pipeline              ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo Available commands:
echo   run_dvc.bat install    - Install DVC and dependencies
echo   run_dvc.bat init       - Initialize DVC repository
echo   run_dvc.bat setup      - Run interactive setup script
echo   run_dvc.bat repro      - Run complete DVC pipeline
echo   run_dvc.bat status     - Check pipeline status
echo   run_dvc.bat dag        - Show pipeline DAG
echo   run_dvc.bat metrics    - Display pipeline metrics
echo   run_dvc.bat test       - Run retrieval tests only
echo   run_dvc.bat demo       - Run demo queries only
echo   run_dvc.bat query      - Start interactive query mode
echo   run_dvc.bat clean      - Clean DVC outputs
echo   run_dvc.bat report     - View pipeline report
echo   run_dvc.bat deps       - Install project dependencies
echo.
goto :end

:install
echo 📦 Installing DVC...
pip install dvc
echo ✅ DVC installed
goto :end

:init
echo 🔧 Initializing DVC...
dvc init
echo ✅ DVC initialized
goto :end

:setup
echo 🚀 Running setup script...
python setup_dvc.py
goto :end

:repro
echo 🏃 Running DVC pipeline...
dvc repro
echo ✅ Pipeline complete
echo.
echo 📊 View results:
echo    - Report: run_dvc.bat report
echo    - Metrics: run_dvc.bat metrics
goto :end

:status
echo 📋 Checking pipeline status...
dvc status
goto :end

:dag
echo 📊 Pipeline DAG:
dvc dag
goto :end

:metrics
echo 📈 Pipeline Metrics:
dvc metrics show
goto :end

:test
echo 🧪 Running retrieval tests...
dvc repro test_retrieval
if exist outputs\retrieval_test_results.txt (
    type outputs\retrieval_test_results.txt
)
goto :end

:demo
echo 🎯 Running demo queries...
dvc repro demo_retrieval
if exist outputs\demo_results.txt (
    type outputs\demo_results.txt
)
goto :end

:query
echo 💬 Starting interactive query mode...
cd rag_llm_app
python -m app.main query
cd ..
goto :end

:report
if exist outputs\PIPELINE_REPORT.md (
    type outputs\PIPELINE_REPORT.md
) else (
    echo ❌ Report not generated yet. Run 'run_dvc.bat repro' first.
)
goto :end

:clean
echo 🧹 Cleaning DVC outputs...
if exist outputs (
    del /q outputs\*.*
)
if exist rag_llm_app\data\documents (
    del /q rag_llm_app\data\documents\*.csv
)
dvc gc -w
echo ✅ Cleaned
goto :end

:deps
echo 📦 Installing project dependencies...
pip install -r rag_llm_app\requirements.txt
echo ✅ Dependencies installed
goto :end

:end
endlocal
