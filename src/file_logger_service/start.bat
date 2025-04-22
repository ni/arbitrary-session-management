@echo off
REM The discovery service uses this script to start the logger service.
REM You can customize this script for your Python setup.

if not exist .venv (
    poetry install --only main
)

.venv\Scripts\python.exe logger_service.py