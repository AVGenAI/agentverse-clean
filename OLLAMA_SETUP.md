# AgentVerse Ollama Integration Guide

## 🦙 Run AI Agents Locally with Ollama!

AgentVerse now supports **Ollama** for running AI agents entirely on your local machine - no cloud API keys required!

## Quick Start

### 1. Install Ollama

**macOS:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from [ollama.ai](https://ollama.ai/download)

### 2. Start Ollama Service
```bash
ollama serve
```

### 3. Pull a Model
```bash
# Recommended models for AgentVerse
ollama pull llama2        # General purpose (7B)
ollama pull mistral       # Fast & efficient (7B) 
ollama pull codellama     # For engineering agents (7B)
ollama pull neural-chat   # For conversational agents (7B)
```

### 4. Configure AgentVerse
Edit `agentverse_api/.env`:
```env
# Enable Ollama (it's enabled by default)
USE_OLLAMA=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Optional: Still set OpenAI as fallback
OPENAI_API_KEY=your_key_here
```

### 5. Start AgentVerse
```bash
./start_agentverse.sh
```

## How It Works

### Intelligent Fallback System
1. **Ollama First**: AgentVerse tries Ollama for local, private AI
2. **OpenAI Fallback**: If Ollama fails, it falls back to OpenAI
3. **Mock Mode**: If both fail, provides contextual mock responses

### Provider Priority
```
Ollama (Local) → OpenAI (Cloud) → Mock Response
```

## Supported Models

### Best Models for AgentVerse

| Model | Size | Best For | Command |
|-------|------|----------|---------|
| **llama2** | 7B | General purpose agents | `ollama pull llama2` |
| **mistral** | 7B | Fast responses, good quality | `ollama pull mistral` |
| **codellama** | 7B | Engineering/coding agents | `ollama pull codellama` |
| **neural-chat** | 7B | Customer support agents | `ollama pull neural-chat` |
| **phi** | 2.7B | Lightweight, fast | `ollama pull phi` |
| **llama2:13b** | 13B | Better quality (needs more RAM) | `ollama pull llama2:13b` |

### Model Selection Tips
- **8GB RAM**: Use 7B models (llama2, mistral)
- **16GB RAM**: Can handle 13B models
- **Apple Silicon**: Excellent performance with Metal acceleration
- **NVIDIA GPU**: CUDA acceleration for faster inference

## Configuration Options

### Basic Configuration
```env
USE_OLLAMA=true              # Enable/disable Ollama
OLLAMA_MODEL=llama2          # Default model
OLLAMA_BASE_URL=http://localhost:11434  # Ollama server
```

### Per-Agent Model Selection (Coming Soon)
```env
# Engineering agents use CodeLlama
OLLAMA_MODEL_ENGINEERING=codellama

# Business agents use Mistral
OLLAMA_MODEL_BUSINESS=mistral

# Data agents use Llama2
OLLAMA_MODEL_DATA=llama2
```

## Performance Tips

### 1. Model Loading
First request to each model will be slower (model loading). Subsequent requests are fast.

### 2. Keep Models Loaded
```bash
# Keep specific model loaded in memory
ollama run llama2 --keep-alive 5h
```

### 3. GPU Acceleration
- **NVIDIA**: Install CUDA for GPU acceleration
- **Apple Silicon**: Metal acceleration works automatically
- **AMD**: ROCm support available

### 4. Resource Usage
Monitor with:
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# See running models
ollama list
```

## Troubleshooting

### "Ollama not available"
1. Check if Ollama is running: `curl http://localhost:11434`
2. Start Ollama: `ollama serve`
3. Check logs: `journalctl -u ollama` (Linux)

### "Model not found"
1. Pull the model: `ollama pull llama2`
2. List available models: `ollama list`
3. Update OLLAMA_MODEL in .env

### Slow Responses
1. First request loads model (normal)
2. Check available RAM
3. Try smaller model (phi, mistral)
4. Enable GPU acceleration

### Connection Refused
1. Check if port 11434 is blocked
2. Ensure Ollama is running
3. Check firewall settings

## Privacy & Security

### 🔒 100% Local Processing
- All conversations stay on your machine
- No data sent to cloud services
- Complete privacy for sensitive discussions

### 🚀 Offline Capable
- Works without internet (after model download)
- No API keys required
- No usage limits or costs

## Advanced Usage

### Custom Models
```bash
# Create custom model with specific parameters
ollama create mymodel -f Modelfile

# Modelfile example:
FROM llama2
PARAMETER temperature 0.7
PARAMETER top_p 0.9
SYSTEM "You are an expert software engineer..."
```

### API Testing
```bash
# Test Ollama directly
curl http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "Hello, how are you?"
}'

# Check AgentVerse health
curl http://localhost:8000/health | jq .llm_providers
```

## Monitoring

The Dashboard shows real-time LLM status:
- 🟢 **"Ollama Active"** - Using local AI
- 🔵 **"OpenAI Active"** - Using cloud AI
- 🔴 **"No LLM"** - Mock mode

## Best Practices

1. **Start with Mistral** - Good balance of speed and quality
2. **Use CodeLlama** - For technical conversations
3. **Enable both providers** - Best reliability
4. **Monitor resources** - Check RAM/GPU usage
5. **Update regularly** - `ollama pull llama2` for updates

## FAQ

**Q: Can I use both Ollama and OpenAI?**
A: Yes! AgentVerse automatically falls back to OpenAI if Ollama fails.

**Q: Which model is best?**
A: Start with `mistral` for speed or `llama2` for quality.

**Q: How much RAM do I need?**
A: 8GB minimum for 7B models, 16GB for 13B models.

**Q: Is it really private?**
A: Yes! Ollama runs 100% locally. No external API calls.

**Q: Can I use custom models?**
A: Yes! Any Ollama model works. Set OLLAMA_MODEL in .env.

## Coming Soon

- [ ] Per-agent model selection
- [ ] Model performance metrics
- [ ] Automatic model downloading
- [ ] Context caching for faster responses
- [ ] Multi-GPU support
- [ ] Quantized models for smaller devices

---

Happy local AI chatting! 🦙✨