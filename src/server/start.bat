@echo off
REM The discovery service uses this script to start the JSON logger service.
REM You can customize this script for your Python setup.

REM Set up the project environment and install dependencies if not already done
if not exist .venv (
    poetry install --only main
)
REM Run the server.
.venv\Scripts\python.exe server.py