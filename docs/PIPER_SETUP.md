# Piper Voice Models Setup

Piper requires voice models to be downloaded separately before synthesis can work.

## Quick Start

### 1. List Available Voices

```bash
source .venv/bin/activate
piper --help
```

### 2. Download Voices via HuggingFace

Piper voices are hosted on HuggingFace. Download them manually:

```bash
# Create directory for voices
mkdir -p ~/.local/share/piper-voices

# Download a voice model (example: en_US-lessac-medium)
cd ~/.local/share/piper-voices

# Download model files from HuggingFace
# Format: https://huggingface.co/rhasspy/piper-voices/resolve/main/[lang]/[region]/[name]/[quality]/
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json

# Download another voice (amy)
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json
```

### 3. Alternative: Browse All Available Voices

Visit: https://huggingface.co/rhasspy/piper-voices/tree/main

Available languages include:
- **English**: en_US, en_GB
- **Chinese**: zh_CN (limited availability)
- **Vietnamese**: vi_VN (limited availability)
- **Spanish, French, German, Italian**, and many more

### 4. Update Voice Paths in Code

Edit `src/services/piper_tts.py` to use downloaded voices:

```python
VOICE_MODELS = {
    "zh_narrator": "en_US-lessac-medium",  # Using English as fallback
    "en_narrator": "en_US-lessac-medium",
    "en_teacher": "en_US-amy-medium",
    # Add more as you download them
}
```

### 5. Set Piper Data Directory (Optional)

```bash
# Tell piper where to find voices
export PIPER_DATA_DIR=~/.local/share/piper-voices

# Or add to .env file
echo "PIPER_DATA_DIR=~/.local/share/piper-voices" >> .env
```

## Recommended Voices for This Project

### English (Best Support)
```bash
cd ~/.local/share/piper-voices
# Lessac - clear male voice
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx{,.json}

# Amy - female voice
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx{,.json}

# Libritts - high quality
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts/high/en_US-libritts-high.onnx{,.json}
```

### Chinese (Limited)
```bash
# Check if available
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/zh/zh_CN/huayan/medium/zh_CN-huayan-medium.onnx{,.json}
```

## Testing After Download

```bash
source .venv/bin/activate
python tests/test_tts_synthesis.py piper
```

Expected output:
```
✓ Synthesis completed successfully!
  Total: 3
  Successful: 3
  Failed: 0
  Output dir: audio/test
  
  ✓ Segment 1: audio/test/test_piper_0001_zh_narrator.wav (1.2s)
  ✓ Segment 2: audio/test/test_piper_0002_vi_teacher.wav (1.5s)
  ✓ Segment 3: audio/test/test_piper_0003_en_narrator.wav (0.8s)
```

## Troubleshooting

### Voice Not Found Error
```
✗ Segment 1: Voice model 'en_US-lessac-medium' not found
```

**Solution**: Download the voice model files (.onnx and .onnx.json) to the piper data directory.

### Permission Errors
```bash
# Make sure directory is writable
chmod -R 755 ~/.local/share/piper-voices
```

### Manual Testing with Piper CLI
```bash
# Test a voice directly
echo "Hello world" | piper --model en_US-lessac-medium --output_file test.wav
```

## Using OpenAI TTS Instead

If Piper setup is too complex, use OpenAI TTS (simpler, but requires API key):

```bash
export OPENAI_API_KEY="sk-..."
python tests/test_tts_synthesis.py openai
```

No voice models needed - works immediately with internet connection.
