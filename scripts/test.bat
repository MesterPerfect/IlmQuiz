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
    echo Please run scripts\setup_env.bat first to set up the test environment.
    popd
    exit /b 1
)

:: Verify pytest is available
"%VENV_DIR%\Scripts\python.exe" -c "import pytest" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pytest is not installed in virtual environment "%VENV_DIR%".
    echo Please run scripts\setup_env.bat to install test dependencies.
    popd
    exit /b 1
)

:: Ensure REPO_ROOT is on PYTHONPATH
if defined PYTHONPATH (
    set "PYTHONPATH=%REPO_ROOT%;%PYTHONPATH%"
) else (
    set "PYTHONPATH=%REPO_ROOT%"
)

echo Running IlmQuiz test suite ...
"%VENV_DIR%\Scripts\python.exe" -m pytest "%REPO_ROOT%\tests" -vv %*
set "EXIT_CODE=%errorlevel%"

popd
exit /b %EXIT_CODE%
