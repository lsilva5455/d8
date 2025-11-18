@echo off
echo Restarting Orchestrator...
cd /d "%~dp0"
set PYTHONPATH=%CD%
venv\Scripts\python.exe test_orchestrator.py
