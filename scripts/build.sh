#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# Locate virtual environment (prefer repository-local .venv)
VENV_DIR=""
if [ -f "$REPO_ROOT/.venv/bin/python" ]; then
    VENV_DIR="$REPO_ROOT/.venv"
elif [ -f "$HOME/.venv/bin/python" ]; then
    VENV_DIR="$HOME/.venv"
fi

if [ -z "$VENV_DIR" ]; then
    echo "[ERROR] Virtual environment not found at \"$REPO_ROOT/.venv\"."
    echo "Please run scripts/setup_env.sh first to set up the build environment."
    exit 1
fi

# Verify cx_Freeze is installed
if ! "$VENV_DIR/bin/python" -c "import cx_Freeze" >/dev/null 2>&1; then
    echo "[ERROR] cx_Freeze is not installed in virtual environment \"$VENV_DIR\"."
    echo "Please run scripts/setup_env.sh to install development dependencies."
    exit 1
fi

# Check if IlmQuiz is currently running
if pgrep -f "IlmQuiz" >/dev/null 2>&1; then
    echo "[ERROR] An instance of IlmQuiz is currently running."
    echo "Running instances lock build artifacts and cause build failure."
    echo "Please close IlmQuiz before building."
    exit 1
fi

# Clean previous build directories before running cx-Freeze
echo "Cleaning previous build artifacts ..."
CLEAN_FAILED=0
if [ -d "$REPO_ROOT/build" ]; then
    echo "Removing build/ ..."
    rm -rf "$REPO_ROOT/build" || CLEAN_FAILED=1
fi
if [ -d "$REPO_ROOT/dist/IlmQuiz" ]; then
    echo "Removing dist/IlmQuiz/ ..."
    rm -rf "$REPO_ROOT/dist/IlmQuiz" || CLEAN_FAILED=1
fi
if [ "$CLEAN_FAILED" -ne 0 ]; then
    echo "[ERROR] Pre-build cleanup failed. Cannot proceed with build while output is locked."
    exit 1
fi

echo "========================================================"
echo "Building IlmQuiz standalone distribution with cx-Freeze"
echo "========================================================"

"$VENV_DIR/bin/python" setup.py build_exe

# Verify executable was produced
TARGET_EXE="$REPO_ROOT/dist/IlmQuiz/IlmQuiz"
if [ ! -f "$TARGET_EXE" ] && [ -f "$TARGET_EXE.exe" ]; then
    TARGET_EXE="$TARGET_EXE.exe"
fi

if [ ! -f "$TARGET_EXE" ]; then
    echo "[ERROR] Build completed but executable was not found at: dist/IlmQuiz/IlmQuiz"
    exit 1
fi

echo "========================================================"
echo "Standalone distribution prepared successfully."
echo "Output directory: dist/IlmQuiz"
echo "Executable: $TARGET_EXE"
echo "========================================================"
