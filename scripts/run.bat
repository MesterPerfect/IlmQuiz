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

:: Ensure REPO_ROOT is on PYTHONPATH
if defined PYTHONPATH (
    set "PYTHONPATH=%REPO_ROOT%;%PYTHONPATH%"
) else (
    set "PYTHONPATH=%REPO_ROOT%"
)

echo Starting IlmQuiz ...
"%VENV_DIR%\Scripts\python.exe" "%REPO_ROOT%\main.py" %*
set "EXIT_CODE=%errorlevel%"

popd
exit /b %EXIT_CODE%
