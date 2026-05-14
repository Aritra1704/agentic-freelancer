#!/bin/bash

# Freelance-OS Launcher
echo "🚀 Launching Freelance-OS Operations..."

# 1. Load Environment
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo "✅ Environment variables loaded."
else
    echo "❌ Error: .env file not found. Please create it with GOOGLE_API_KEY."
    exit 1
fi

# 2. Setup Python Path
export PYTHONPATH=$PYTHONPATH:$(pwd)
echo "✅ Python Path set to $(pwd)"

# 3. Check Ollama
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama is running."
else
    echo "⚠️ Warning: Ollama is not running. Local delegation will fail."
fi

# 3. Run the System
source venv/bin/activate
python3 main.py full-cycle
