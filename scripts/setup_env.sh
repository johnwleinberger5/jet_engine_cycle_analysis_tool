#!/usr/bin/env bash
set -e

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

echo "Installing dependencies..."
"$PIP" install --upgrade pip
"$PIP" install -e ".[dev]"

echo ""
echo "Done. Activate your environment with:"
if [ -f "$VENV_DIR/Scripts/activate" ]; then
    echo "  source .venv/Scripts/activate"
else
    echo "  source .venv/bin/activate"
fi
