@echo off
REM The discovery service uses this script to install the dependencies
REM for the file logger service. You can customize this script for your Python setup.

poetry install --only main