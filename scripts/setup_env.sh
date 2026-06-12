#!/usr/bin/env bash
set -euo pipefail

VENV_DIR=".venv"

# Create venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists, skipping creation."
fi

# Resolve pip path (Windows: Scripts/, Linux/Mac: bin/)
if [ -f "$VENV_DIR/Scripts/pip" ]; then
    PIP="$VENV_DIR/Scripts/pip"
elif [ -f "$VENV_DIR/bin/pip" ]; then
    PIP="$VENV_DIR/bin/pip"
else
    echo "ERROR: Could not find pip in virtual environment."
    exit 1
fi

echo "Upgrading pip..."
"$VENV_DIR/Scripts/python" -m pip install --upgrade pip 2>/dev/null \
    || "$VENV_DIR/bin/python" -m pip install --upgrade pip

echo "Installing project dependencies..."
"$PIP" install -e ".[dev]"

echo "Verifying installation..."
"$VENV_DIR/Scripts/python" -c "import pytest; import pipeline" 2>/dev/null \
    || "$VENV_DIR/bin/python" -c "import pytest; import pipeline"

echo ""
echo "Setup complete. Activate your environment with:"
if [ -f "$VENV_DIR/Scripts/activate" ]; then
    echo "  source .venv/Scripts/activate"
else
    echo "  source .venv/bin/activate"
fi
