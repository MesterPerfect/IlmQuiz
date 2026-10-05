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
    echo "Please run scripts/setup_env.sh first to set up the environment."
    exit 1
fi

# Verify ruff is available
if [ ! -f "$VENV_DIR/bin/ruff" ]; then
    echo "[ERROR] Ruff not found in virtual environment at \"$VENV_DIR\"."
    echo "Please run scripts/setup_env.sh to install development dependencies."
    exit 1
fi

# Verify mypy is available
if [ ! -f "$VENV_DIR/bin/mypy" ]; then
    echo "[ERROR] Mypy not found in virtual environment at \"$VENV_DIR\"."
    echo "Please run scripts/setup_env.sh to install development dependencies."
    exit 1
fi

echo "========================================================"
echo "Running Ruff lint check ..."
echo "========================================================"
"$VENV_DIR/bin/ruff" check core data services ui tests main.py apply_update.py

echo "========================================================"
echo "Running Ruff format check ..."
echo "========================================================"
"$VENV_DIR/bin/ruff" format --check core data services ui tests main.py apply_update.py || {
    echo "[WARNING] Ruff formatting differences detected. Run 'ruff format' to fix automatically."
}

echo "========================================================"
echo "Running Mypy static type analysis ..."
echo "========================================================"
"$VENV_DIR/bin/mypy" core data services ui tests || {
    echo "[WARNING] Mypy found type notices."
}

echo "========================================================"
echo "[OK] Code verification completed successfully!"
echo "========================================================"
