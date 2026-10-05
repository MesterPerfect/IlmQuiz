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
    echo Please run scripts\setup_env.bat first to set up the build environment.
    popd
    exit /b 1
)

:: Verify cx_Freeze is installed
"%VENV_DIR%\Scripts\python.exe" -c "import cx_Freeze" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] cx_Freeze is not installed in virtual environment "%VENV_DIR%".
    echo Please run scripts\setup_env.bat to install development dependencies.
    popd
    exit /b 1
)

:: Check if IlmQuiz.exe is currently running and locking previous build output
tasklist /FI "IMAGENAME eq IlmQuiz.exe" 2>nul | find /I "IlmQuiz.exe" >nul 2>&1
if not errorlevel 1 (
    echo [ERROR] IlmQuiz.exe is currently running.
    echo Running instances lock build artifacts and cause cx-Freeze to fail.
    echo Please close IlmQuiz.exe before building.
    popd
    exit /b 1
)

:: Clean previous build directories before running cx-Freeze
echo Cleaning previous build artifacts ...
set "CLEAN_FAILED=0"
if exist "%REPO_ROOT%\build" (
    echo Removing build\ ...
    rmdir /s /q "%REPO_ROOT%\build" >nul 2>&1
    if exist "%REPO_ROOT%\build" (
        echo [ERROR] Failed to remove directory: "%REPO_ROOT%\build"
        set "CLEAN_FAILED=1"
    )
)
if exist "%REPO_ROOT%\dist\IlmQuiz" (
    echo Removing dist\IlmQuiz\ ...
    rmdir /s /q "%REPO_ROOT%\dist\IlmQuiz" >nul 2>&1
    if exist "%REPO_ROOT%\dist\IlmQuiz" (
        echo [ERROR] Failed to remove directory: "%REPO_ROOT%\dist\IlmQuiz"
        set "CLEAN_FAILED=1"
    )
)
if "!CLEAN_FAILED!"=="1" (
    echo [ERROR] Pre-build cleanup failed. Cannot proceed with build while output is locked.
    popd
    exit /b 1
)

echo ========================================================
echo Building IlmQuiz standalone distribution with cx-Freeze
echo ========================================================

"%VENV_DIR%\Scripts\python.exe" setup.py build_exe
if errorlevel 1 (
    echo [ERROR] cx-Freeze build failed.
    popd
    exit /b 1
)

:: Verify executable was produced
if not exist "%REPO_ROOT%\dist\IlmQuiz\IlmQuiz.exe" (
    echo [ERROR] Build completed but executable was not found at: dist\IlmQuiz\IlmQuiz.exe
    popd
    exit /b 1
)

echo ========================================================
echo Standalone distribution prepared successfully.
echo Output directory: dist\IlmQuiz
echo Executable: dist\IlmQuiz\IlmQuiz.exe
echo ========================================================

:: Locate Inno Setup compiler (ISCC.exe)
set "ISCC_EXE="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC_EXE=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC_EXE if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC_EXE=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC_EXE if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" set "ISCC_EXE=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
if not defined ISCC_EXE (
    for /f "delims=" %%i in ('where iscc.exe 2^>nul') do set "ISCC_EXE=%%i"
)

if not defined ISCC_EXE (
    echo [INFO] Inno Setup compiler ISCC.exe not found.
    echo Standalone executable is available at: dist\IlmQuiz\IlmQuiz.exe
    echo If you want to generate the Windows installer, install Inno Setup 6.
    popd
    exit /b 0
)

echo ========================================================
echo Compiling Inno Setup installer with:
echo "%ISCC_EXE%"
echo ========================================================

if not exist "%REPO_ROOT%\ilmquiz_setup.iss" (
    echo [ERROR] Inno Setup script not found at: ilmquiz_setup.iss
    popd
    exit /b 1
)

"%ISCC_EXE%" "%REPO_ROOT%\ilmquiz_setup.iss"
if errorlevel 1 (
    echo [ERROR] Inno Setup installer compilation failed.
    popd
    exit /b 1
)

echo ========================================================
echo Build and Installer compilation succeeded!
echo Standalone App: dist\IlmQuiz\IlmQuiz.exe
echo Installer Directory: build_installer\
echo ========================================================

popd
exit /b 0
