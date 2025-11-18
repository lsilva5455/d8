#!/bin/bash
# Setup script for The Hive GitHub Codespaces
# This script is run automatically when the Codespace is created

set -e  # Exit on error

echo "🐝 Setting up The Hive development environment..."
echo "================================================="
echo ""

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p data/genomes
mkdir -p data/metrics
mkdir -p data/logs
mkdir -p data/chromadb
mkdir -p legacy_code
mkdir -p tests/{unit,integration,e2e}

# Ensure directory permissions
chmod -R 755 data/
chmod -R 755 legacy_code/

echo "✅ Directories created successfully"
echo ""

# Copy .env.example to .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "⚠️  IMPORTANT: You need to add your GROQ_API_KEY to the .env file"
else
    echo "✅ .env file already exists"
fi
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt
echo "✅ Python dependencies installed"
echo ""

# Install Ollama if not present
echo "🦙 Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
    echo "✅ Ollama installed successfully"
else
    echo "✅ Ollama is already installed"
fi
echo ""

# Start Ollama service in background
echo "🚀 Starting Ollama service..."
ollama serve > /tmp/ollama.log 2>&1 &
OLLAMA_PID=$!
echo "✅ Ollama service started (PID: $OLLAMA_PID)"
echo "   Logs available at: /tmp/ollama.log"
echo ""

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama is ready!"
        break
    fi
    echo -n "."
    sleep 2
done
echo ""

# Pull DeepSeek model (this may take a while for the first time)
echo "🤖 Pulling DeepSeek model (deepseek-coder:33b)..."
echo "⚠️  This is a large model (~19GB) and may take 10-30 minutes depending on your connection"
echo "   The Codespace will be ready to use even while the model downloads in the background"
echo ""

# Pull model in background to not block the setup
(
    ollama pull deepseek-coder:33b > /tmp/ollama-pull.log 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ DeepSeek model downloaded successfully" >> /tmp/setup-status.log
        echo "$(date): DeepSeek model ready" >> data/logs/model-status.log
    else
        echo "⚠️  DeepSeek model download encountered an issue. Check /tmp/ollama-pull.log" >> /tmp/setup-status.log
        echo "$(date): DeepSeek model download failed" >> data/logs/model-status.log
    fi
) &

echo "✅ DeepSeek model download started in background"
echo "   Monitor progress: tail -f /tmp/ollama-pull.log"
echo "   Check status: ollama list"
echo ""

# Create a convenience script for checking model status
cat > /tmp/check-model.sh << 'EOF'
#!/bin/bash
echo "=== Ollama Service Status ==="
if pgrep -x ollama > /dev/null; then
    echo "✅ Ollama service is running"
else
    echo "❌ Ollama service is not running"
fi
echo ""

echo "=== Available Models ==="
ollama list
echo ""

echo "=== Model Download Progress ==="
if [ -f /tmp/ollama-pull.log ]; then
    tail -20 /tmp/ollama-pull.log
else
    echo "No download log found"
fi
EOF
chmod +x /tmp/check-model.sh

echo "================================================="
echo "✅ Setup Complete!"
echo "================================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Add your GROQ API key to .env file:"
echo "   edit .env and set GROQ_API_KEY=your_key_here"
echo "   Get your key from: https://console.groq.com/"
echo ""
echo "2. Monitor DeepSeek model download (optional):"
echo "   /tmp/check-model.sh"
echo "   OR"
echo "   tail -f /tmp/ollama-pull.log"
echo ""
echo "3. Start The Hive:"
echo "   python app/main.py"
echo ""
echo "4. Test the API:"
echo "   curl http://localhost:5000/"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Project overview and API docs"
echo "   - .devcontainer/README.md - Codespaces usage guide"
echo "   - docs/ - Additional documentation"
echo ""
echo "💡 Useful Commands:"
echo "   pytest                    # Run tests"
echo "   /tmp/check-model.sh       # Check Ollama status"
echo "   ollama list               # List available models"
echo "   ollama ps                 # Show running models"
echo ""
echo "🐝 Happy coding!"
echo ""
