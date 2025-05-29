@echo off
REM Check if a directory argument is provided
IF "%~1"=="" (
    echo Usage: %~nx0 [directory]
    exit /b 1
)

cd /d "%~1" || (
    echo Failed to change directory to %~1
    exit /b 1
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat || (
    echo Failed to activate virtual environment.
    exit /b 1
)

echo.
set /p CONTINUE="Press Enter to run: poetry run ni-python-styleguide lint"
poetry run ni-python-styleguide lint

echo.
set /p CONTINUE="Press Enter to run: poetry run ni-python-styleguide fix"
poetry run ni-python-styleguide fix

echo.
set /p CONTINUE="Press Enter to run: poetry run ni-python-styleguide lint (post-fix check)"
poetry run ni-python-styleguide lint

echo.
set /p CONTINUE="Press Enter to run: poetry run bandit -c pyproject.toml -r ."
poetry run bandit -c pyproject.toml -r .

echo.
set /p CONTINUE="Press Enter to run: poetry run mypy ."
poetry run mypy .

echo.
echo All checks completed.
