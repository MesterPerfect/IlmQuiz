@echo off
setlocal EnableDelayedExpansion

set "REPO_ROOT=%~dp0.."
pushd "%REPO_ROOT%"

echo ========================================================
echo IlmQuiz - Development Environment Setup
echo ========================================================

:: Check for Python
where python >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python"
) else (
    where py >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_CMD=py -3"
    ) else (
        echo [ERROR] Python is not found in PATH or via the 'py' launcher.
        echo Please install Python 3.11 or later and ensure it is added to PATH.
        popd
        exit /b 1
    )
)

echo Using Python: %PYTHON_CMD%
%PYTHON_CMD% --version
if errorlevel 1 (
    echo [ERROR] Failed to execute Python.
    popd
    exit /b 1
)

:: Create repository-local virtual environment if missing
set "VENV_DIR=%REPO_ROOT%\.venv"
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Creating virtual environment in .venv ...
    %PYTHON_CMD% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment at "%VENV_DIR%".
        popd
        exit /b 1
    )
    echo Virtual environment created.
) else (
    echo Virtual environment already exists at "%VENV_DIR%".
)

:: Upgrade pip
echo Upgrading pip ...
"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 (
    echo [WARNING] Failed to upgrade pip, proceeding with package installation...
)

:: Install production and development dependencies
echo Installing IlmQuiz dependencies ...
"%VENV_DIR%\Scripts\python.exe" -m pip install -r "%REPO_ROOT%\requirements.txt" -r "%REPO_ROOT%\requirements-dev.txt"
if errorlevel 1 (
    echo [ERROR] Dependency installation failed.
    popd
    exit /b 1
)

:: Verify IlmQuiz core modules import
echo Verifying IlmQuiz dependencies ...
"%VENV_DIR%\Scripts\python.exe" -c "import PySide6, core, data, services, ui; print('[OK] All IlmQuiz packages loaded successfully.')"
if errorlevel 1 (
    echo [ERROR] Verification failed: Unable to import core IlmQuiz modules from "%VENV_DIR%".
    popd
    exit /b 1
)

echo ========================================================
echo IlmQuiz environment setup completed successfully!
echo You can now run:
echo   scripts\run.bat       - Launch the application
echo   scripts\test.bat      - Run test suite
echo   scripts\check.bat     - Run linter and type checks
echo   scripts\build.bat     - Build standalone package and installer
echo ========================================================

popd
exit /b 0
