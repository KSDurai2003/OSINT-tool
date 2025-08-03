#!/bin/bash

# Paths
path="$HOME/iget"
venv_path="$path/venv"
REQ="requirements.txt"
script="osint.sh"
main_script="osint.py"
cmd_path="/usr/local/bin/osint"
  # Target path for the main script

# Create project folder
mkdir -p "$path"

# Create virtual environment
echo "🆕 Creating virtual environment..."
python3 -m venv "$venv_path"

# Activate and install dependencies
echo "📦 Installing dependencies..."
if [ -f "$REQ" ]; then
    "$venv_path/bin/pip" install --upgrade pip
    "$venv_path/bin/pip" install -r "$REQ"
else
    echo "❗ $REQ not found, skipping dependency installation."
fi

# Copy your launcher script
if [ -f "$script" ]; then
    cp "$script" "$path"
    chmod +x "$path/$script"
else
    echo "❗ $script not found, skipping init script."
fi

# Copy and make executable the main Python script
if [ -f "$main_script" ]; then
    cp "$main_script" "$path"
    chmod +x "$cmd_main"
else
    echo "❗ $main_script not found, skipping Python script."
fi

# Create a symlink to the launcher
echo "🔗 Creating global symlink (may require sudo)..."
sudo ln -sf "$path/$script" "$cmd_path"

# Prompt user to run
: <<'END_COMMENT'
read -p "▶️ Do you want to run OSINT now? (y/n): " des
if [[ "$des" =~ ^[Yy]$ ]]; then
    "$cmd_path"
else
    echo "🚪 Exiting..."
    exit 0
fi
END_COMMENT
