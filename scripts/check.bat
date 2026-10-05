@echo off
setlocal EnableDelayedExpansion

set "REPO_ROOT=%~dp0.."
pushd "%REPO_ROOT%"

:: Locate virtual environment (prefer repository-local .venv)
set "VENV_DIR="
if exist "%REPO_ROOT%\.venv\Scripts\python.exe" (
    set "VENV_DIR=%REPO_ROOT%\.venv"
) else if exist "%USERPROFILE%\.venv\Scripts\python.exe" (
    set "VENV_DIR=%USERPROFILE%\.venv"
)

if "%VENV_DIR%"=="" (
    echo [ERROR] Virtual environment not found at "%REPO_ROOT%\.venv".
    echo Please run scripts\setup_env.bat first to set up the environment.
    popd
    exit /b 1
)

:: Verify ruff is available
if not exist "%VENV_DIR%\Scripts\ruff.exe" (
    echo [ERROR] Ruff not found in virtual environment at "%VENV_DIR%".
    echo Please run scripts\setup_env.bat first to install development dependencies.
    popd
    exit /b 1
)

:: Verify mypy is available
if not exist "%VENV_DIR%\Scripts\mypy.exe" (
    echo [ERROR] Mypy not found in virtual environment at "%VENV_DIR%".
    echo Please run scripts\setup_env.bat first to install development dependencies.
    popd
    exit /b 1
)

echo ========================================================
echo Running Ruff lint check ...
echo ========================================================
"%VENV_DIR%\Scripts\ruff.exe" check core data services ui tests main.py apply_update.py
if errorlevel 1 (
    echo [ERROR] Ruff lint check failed.
    popd
    exit /b 1
)

echo ========================================================
echo Running Ruff format check ...
echo ========================================================
"%VENV_DIR%\Scripts\ruff.exe" format --check core data services ui tests main.py apply_update.py
if errorlevel 1 (
    echo [WARNING] Ruff formatting differences detected. Run 'ruff format' to fix automatically.
)

echo ========================================================
echo Running Mypy static type analysis ...
echo ========================================================
"%VENV_DIR%\Scripts\mypy.exe" core data services ui tests
if errorlevel 1 (
    echo [WARNING] Mypy found type notices.
)

echo ========================================================
echo [OK] Code verification completed successfully!
echo ========================================================
popd
exit /b 0
