@echo off

REM Set up the project environment and install dependencies if not already done
if not exist .venv (
    poetry install --only main
)