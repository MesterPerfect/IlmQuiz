#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

echo "========================================================"
echo "IlmQuiz - Development Environment Setup (macOS / Linux)"
echo "========================================================"

# Check for Python 3.11+
PYTHON_CMD=""
for cmd in python3 python; do
    if command -v "$cmd" >/dev/null 2>&1; then
        if "$cmd" -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
            PYTHON_CMD="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "[ERROR] Python 3.11 or later was not found in PATH."
    echo "Please install Python 3.11+ using your package manager (e.g. brew, apt, dnf, pacman)."
    exit 1
fi

echo "Using Python: $PYTHON_CMD ($("$PYTHON_CMD" --version))"

# Create repository-local virtual environment if missing
VENV_DIR="$REPO_ROOT/.venv"
if [ ! -f "$VENV_DIR/bin/python" ]; then
    echo "Creating virtual environment in .venv ..."
    "$PYTHON_CMD" -m venv "$VENV_DIR"
    echo "Virtual environment created."
else
    echo "Virtual environment already exists at \"$VENV_DIR\"."
fi

# Upgrade pip
echo "Upgrading pip ..."
"$VENV_DIR/bin/python" -m pip install --upgrade pip || {
    echo "[WARNING] Failed to upgrade pip, proceeding with package installation..."
}

# Install production and development dependencies
echo "Installing IlmQuiz dependencies ..."
"$VENV_DIR/bin/python" -m pip install -r "$REPO_ROOT/requirements.txt" -r "$REPO_ROOT/requirements-dev.txt"

# Verify IlmQuiz dependencies
echo "Verifying IlmQuiz dependencies ..."
"$VENV_DIR/bin/python" -c "import PySide6, core, data, services, ui; print('[OK] All IlmQuiz packages loaded successfully.')"

echo "========================================================"
echo "IlmQuiz environment setup completed successfully!"
echo "You can now run:"
echo "  scripts/run.sh       - Launch the application"
echo "  scripts/test.sh      - Run test suite"
echo "  scripts/check.sh     - Run linter and type checks"
echo "  scripts/build.sh     - Build standalone package with cx-Freeze"
echo "========================================================"
