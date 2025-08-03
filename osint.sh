#!/bin/bash

# Try to fix invalid working directory if we're in a deleted folder
cd "$PWD" 2>/dev/null || cd "$HOME"

# Resolve directory of this script even if symlinked
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"

# Define paths
VENV_PATH="$SCRIPT_DIR/venv"
PYTHON_SCRIPT="$SCRIPT_DIR/osint.py"

# Activate virtual environment
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
else
    echo "❌ Virtual environment not found at $VENV_PATH"
    exit 1
fi

# Run Python script
if [ -f "$PYTHON_SCRIPT" ]; then
    python "$PYTHON_SCRIPT"
else
    echo "❌ Python script not found at $PYTHON_SCRIPT"
    deactivate
    exit 1
fi

# Deactivate if defined
if declare -f deactivate > /dev/null; then
    deactivate
fi
