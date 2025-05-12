@echo off
REM The discovery service uses this script to start the file logger service.
REM You can customize this script for your Python setup.

REM Change to src directory.
cd ..
REM Install the dependencies.
poetry install
REM Run the server.
.venv\Scripts\python.exe file_logger_service/server.py