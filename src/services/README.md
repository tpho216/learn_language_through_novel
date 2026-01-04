# TTS Services

This directory contains TTS (Text-to-Speech) provider implementations for synthesizing audio from text segments.

## Architecture

The TTS system uses a provider pattern with an abstract base class (`TTSProvider`) that can be implemented for different TTS backends.

### Available Providers

#### 1. Piper TTS (`piper_tts.py`)
- **Type**: Local neural TTS
- **Pros**: Free, fast, works offline, good quality
- **Cons**: Requires local installation, limited voice options
- **Output format**: WAV
- **Setup**: Install Piper from https://github.com/rhasspy/piper

```bash
# Install Piper (example for Linux)
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz
tar -xzf piper_amd64.tar.gz
sudo mv piper /usr/local/bin/
```

#### 2. OpenAI TTS (`openai_tts.py`)
- **Type**: Cloud API
- **Pros**: High quality, natural voices, multiple languages
- **Cons**: Costs money, requires internet, API rate limits
- **Output format**: MP3
- **Setup**: Set `OPENAI_API_KEY` environment variable

```bash
export OPENAI_API_KEY="sk-..."
```

## Usage

### Via API Endpoint

```python
import httpx

# Prepare segments (from /llm/prepare_tts_segments endpoint)
segments = [...]

# Synthesize with Piper
response = httpx.post("http://localhost:8000/tts/synthesize", json={
    "segments": segments,
    "output_dir": "audio/chapter_001",
    "provider": "piper",
    "filename_prefix": "ch001"
})

# Synthesize with OpenAI
response = httpx.post("http://localhost:8000/tts/synthesize", json={
    "segments": segments,
    "output_dir": "audio/chapter_001",
    "provider": "openai",
    "openai_model": "hd",  # or "standard"
    "filename_prefix": "ch001"
})
```

### Voice Mapping

The system maps semantic voice names to provider-specific voices:

**Semantic voices**:
- `narrator` - Story narration
- `teacher` - Educational/explanatory content
- `character` - Character dialogue

**Language codes**:
- `zh` - Chinese
- `vi` - Vietnamese
- `en` - English

## Adding a New Provider

1. Create a new file in `src/services/` (e.g., `my_tts.py`)
2. Implement the `TTSProvider` abstract class:

```python
from .tts_provider import TTSProvider

class MyTTSProvider(TTSProvider):
    async def synthesize(self, text, output_path, voice, lang, style, **kwargs):
        # Implementation here
        pass
    
    def get_available_voices(self, lang=None):
        # Return available voices
        pass
```

3. Add provider to `main.py` synthesis endpoint:

```python
elif req.provider == "mytts":
    provider = MyTTSProvider()
```

## Configuration

### Environment Variables

```bash
# OpenAI TTS (required for OpenAI provider)
OPENAI_API_KEY="sk-..."

# Piper TTS (optional, defaults shown)
PIPER_BINARY="piper"
PIPER_MODELS_DIR="~/.local/share/piper-tts"
```

### Request Options

```json
{
  "segments": [...],
  "output_dir": "audio",
  "provider": "piper|openai",
  "piper_binary": "/path/to/piper",
  "openai_model": "standard|hd",
  "filename_prefix": "segment"
}
```

## Output Format

Audio files are named: `{prefix}_{order:04d}_{lang}_{voice}.{ext}`

Example: `ch001_0001_zh_narrator.wav`

## Testing

```bash
# Test Piper
python scripts/test_tts_synthesis.py piper

# Test OpenAI
python scripts/test_tts_synthesis.py openai
```
