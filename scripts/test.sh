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
    echo "Please run scripts/setup_env.sh first to set up the test environment."
    exit 1
fi

# Verify pytest is available
if ! "$VENV_DIR/bin/python" -c "import pytest" >/dev/null 2>&1; then
    echo "[ERROR] pytest is not installed in virtual environment \"$VENV_DIR\"."
    echo "Please run scripts/setup_env.sh to install test dependencies."
    exit 1
fi

# Ensure REPO_ROOT is on PYTHONPATH
if [ -n "$PYTHONPATH" ]; then
    export PYTHONPATH="$REPO_ROOT:$PYTHONPATH"
else
    export PYTHONPATH="$REPO_ROOT"
fi

echo "Running IlmQuiz test suite ..."
exec "$VENV_DIR/bin/python" -m pytest "$REPO_ROOT/tests" -vv "$@"
