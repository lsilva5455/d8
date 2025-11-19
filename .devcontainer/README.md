# 🐝 The Hive - GitHub Codespaces Guide

This directory contains the configuration for running The Hive project in GitHub Codespaces, providing a complete, pre-configured development environment in the cloud.

## 🎯 What This Devcontainer Does

This devcontainer configuration automatically sets up a complete development environment with:

- **Python 3.11** runtime environment
- **All project dependencies** installed from `requirements.txt`
- **Ollama** local LLM server for DeepSeek evolution engine
- **DeepSeek-coder:33b model** (downloads in background)
- **Flask development server** ready to run on port 7001
- **VS Code extensions** for Python development (Pylance, Black, GitLens)
- **Project structure** with all necessary directories
- **Environment configuration** from `.env.example`

## 🚀 Getting Started with GitHub Codespaces

### 1. Create a Codespace

**Via GitHub Web UI:**
1. Go to the repository: https://github.com/lsilva5455/d8
2. Click the green **Code** button
3. Select the **Codespaces** tab
4. Click **Create codespace on main** (or your branch)

**Via GitHub CLI:**
```bash
gh codespace create --repo lsilva5455/d8
```

The Codespace will automatically:
- Clone the repository
- Build the development container
- Install all dependencies
- Set up the project structure
- Start Ollama service
- Begin downloading the DeepSeek model

⏱️ **Initial setup takes 3-5 minutes** (model downloads continue in background)

### 2. Configure API Keys

Once your Codespace is ready, you **must** add your Groq API key:

```bash
# Open the .env file
code .env

# Add your Groq API key
GROQ_API_KEY=gsk_your_actual_key_here
```

**Get your Groq API key:**
- Visit: https://console.groq.com/
- Sign up or log in
- Go to API Keys section
- Create a new key

### 3. Verify Setup

Check that everything is ready:

```bash
# Check Ollama service
/tmp/check-model.sh

# Or manually check
ollama list

# Check if DeepSeek model is available
ollama list | grep deepseek-coder
```

If the model is still downloading, you'll see progress in:
```bash
tail -f /tmp/ollama-pull.log
```

## 🎮 Running the Project

### Start The Hive Server

```bash
python app/main.py
```

The Flask server will start on port 7001. GitHub Codespaces automatically forwards this port and provides a URL.

### Access the API

GitHub Codespaces will show a notification with the forwarded port URL, or you can:

1. Click the **PORTS** tab in VS Code
2. Find port 7001 (Flask API Server)
3. Click the globe icon to open in browser
4. Or hover and copy the forwarded URL

## 📡 Testing the API

### Health Check

```bash
curl http://localhost:7001/
```

Expected response:
```json
{
  "status": "online",
  "message": "The Hive is operational",
  "version": "1.0",
  "components": {
    "agent_pool": "ready",
    "evolution_engine": "ready",
    "d8_genesis": "ready"
  }
}
```

### List Agents

```bash
curl http://localhost:7001/api/agents
```

### Initialize Population

```bash
curl -X POST http://localhost:7001/api/initialize
```

### Trigger Evolution

```bash
curl -X POST http://localhost:7001/api/evolve
```

### Agent Action

```bash
curl -X POST http://localhost:7001/api/agents/<agent_id>/act \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "generate_content",
    "input_data": {
      "niche": "AI tools",
      "target_audience": "developers"
    }
  }'
```

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/unit/test_agent.py

# Run with verbose output
pytest -v
```

## 🔧 Troubleshooting

### DeepSeek Model Not Available

**Issue:** The DeepSeek model is still downloading or failed to download.

**Solution:**
```bash
# Check download status
/tmp/check-model.sh

# Check download logs
tail -f /tmp/ollama-pull.log

# Manually pull the model
ollama pull deepseek-coder:33b

# Or use a smaller alternative (faster download)
ollama pull deepseek-coder:6.7b
# Then update .env:
# DEEPSEEK_MODEL=deepseek-coder:6.7b
```

### Ollama Service Not Running

**Issue:** Ollama service is not responding.

**Solution:**
```bash
# Check if Ollama is running
pgrep ollama

# If not running, start it manually
ollama serve > /tmp/ollama.log 2>&1 &

# Check logs
tail -f /tmp/ollama.log
```

### Port 7001 Already in Use

**Issue:** Flask can't start because port 7001 is occupied.

**Solution:**
```bash
# Find process using port 7001
lsof -i :7001

# Kill the process (replace PID)
kill -9 <PID>

# Or change Flask port in .env
FLASK_PORT=5001
```

### Missing GROQ_API_KEY

**Issue:** API returns authentication errors.

**Solution:**
```bash
# Check if key is set
grep GROQ_API_KEY .env

# If empty or missing, add it
echo "GROQ_API_KEY=gsk_your_key_here" >> .env

# Or edit the file
code .env
```

### Out of Memory

**Issue:** Codespace runs out of memory when running DeepSeek.

**Solution:**
- The devcontainer requests 8GB RAM minimum
- If still experiencing issues, consider using a smaller model:
  ```bash
  ollama pull deepseek-coder:6.7b
  # Update .env: DEEPSEEK_MODEL=deepseek-coder:6.7b
  ```
- Or request a machine type upgrade in Codespaces settings

### ChromaDB Issues

**Issue:** Vector database errors.

**Solution:**
```bash
# Clear ChromaDB cache
rm -rf data/chromadb/*

# Restart the application
python app/main.py
```

## 📊 Performance Notes

### Resource Requirements

- **Minimum:** 4 cores, 8GB RAM, 32GB storage
- **Recommended:** 8 cores, 16GB RAM, 64GB storage
- **DeepSeek Model Size:** ~19GB for 33B parameter model
- **Alternative Models:**
  - `deepseek-coder:6.7b` - ~4GB (faster, less capable)
  - `deepseek-coder:1.3b` - ~1GB (fastest, basic capability)

### Response Times

- **Groq API (Agent Actions):** 50-200ms
- **DeepSeek Evolution (Local):** 10-30 seconds
- **Initial Model Download:** 10-30 minutes (one-time, background)

### Codespace Machine Types

GitHub offers different machine types:
- **2-core:** Too small for this project
- **4-core:** Minimum, works with smaller models
- **8-core:** Recommended for full experience
- **16-core:** Optimal for heavy development

Configure in repository settings or when creating the Codespace.

## 🛠️ Development Tools Included

### VS Code Extensions

- **Python** - Python language support
- **Pylance** - Advanced Python IntelliSense
- **GitLens** - Git visualization and exploration
- **Black Formatter** - Code formatting
- **Flake8** - Linting
- **autoDocstring** - Generate docstrings
- **Better Comments** - Enhanced comment highlighting
- **Path Intellisense** - File path autocompletion

### Python Tools

All tools from `requirements.txt` including:
- `pytest` - Testing framework
- `black` - Code formatter
- `flake8` - Linter
- `mypy` - Type checker
- `rich` - Beautiful terminal output
- And more...

## 📚 Additional Resources

### Project Documentation

- **[README.md](../README.md)** - Main project documentation
- **[D8-GENESIS Module](../docs/D8_GENESIS_MODULE.md)** - Self-coding system
- **[Monetization Strategy](../ESTRATEGIA_MONETIZACION.md)** - Business analysis

### External Resources

- **Groq Console:** https://console.groq.com/
- **Ollama Documentation:** https://ollama.ai/docs
- **GitHub Codespaces Docs:** https://docs.github.com/en/codespaces
- **Flask Documentation:** https://flask.palletsprojects.com/

## 💡 Tips and Best Practices

### Saving Your Work

- All changes are automatically saved to the Codespace
- Commit and push regularly to save to GitHub:
  ```bash
  git add .
  git commit -m "Your changes"
  git push
  ```

### Stopping/Starting Codespaces

- **Pause:** Codespaces auto-pause after 30 minutes of inactivity
- **Resume:** Just reopen from GitHub - state is preserved
- **Stop:** Manually stop from GitHub Codespaces UI to save costs
- **Delete:** Delete when done to free resources

### Cost Management

- Codespaces have free monthly hours based on your GitHub plan
- Larger machines consume hours faster
- Stop Codespaces when not in use
- Consider using local development for extended sessions

### Background Processes

The setup script starts Ollama in the background. To manage it:

```bash
# Check Ollama status
pgrep ollama

# Restart Ollama if needed
pkill ollama
ollama serve > /tmp/ollama.log 2>&1 &

# Check logs
tail -f /tmp/ollama.log
```

### Working with Models

```bash
# List available models
ollama list

# Pull additional models
ollama pull codellama:13b

# Remove a model to free space
ollama rm deepseek-coder:33b

# Show running models
ollama ps
```

## 🔐 Security Notes

- **Never commit `.env` file** - It's in `.gitignore`
- **API keys are private** - Don't share or expose them
- **Use environment variables** - For all sensitive configuration
- **Codespaces are isolated** - Your code runs in a secure container

## 🆘 Getting Help

If you encounter issues:

1. **Check logs:**
   - Flask: Terminal output
   - Ollama: `/tmp/ollama.log`
   - Setup: `/tmp/setup-status.log`
   - Model download: `/tmp/ollama-pull.log`

2. **Run diagnostics:**
   ```bash
   /tmp/check-model.sh
   ```

3. **Rebuild Codespace:**
   - From Command Palette (Cmd/Ctrl+Shift+P)
   - Select "Codespaces: Rebuild Container"

4. **Check repository issues:**
   - https://github.com/lsilva5455/d8/issues

5. **Review main README:**
   - [README.md](../README.md)

## 🎉 You're All Set!

You now have a fully functional AI agent development environment running in the cloud. Start exploring, experimenting, and building with The Hive!

Happy coding! 🐝
