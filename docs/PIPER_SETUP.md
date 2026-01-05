# Piper Voice Models Setup

Piper requires voice models to be downloaded separately before synthesis can work.

## Prerequisites

Before following this guide, ensure you have:

1. **Python 3.12** virtual environment activated (see main README.md)
2. **Piper TTS installed** (`pip install -r requirements.txt`)
3. **System audio libraries**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install -y libsndfile1
   
   # macOS
   brew install libsndfile
   ```

## Quick Start

### 1. Download Voice Models (Recommended Method)

Use the official Piper download command (easiest):

```bash
source .venv/bin/activate

# Download English voices
python3 -m piper.download_voices en_US-lessac-medium
python3 -m piper.download_voices en_US-amy-medium

# Download Vietnamese voice
python3 -m piper.download_voices vi_VN-vais1000-medium

# Download Chinese voice
python3 -m piper.download_voices zh_CN-huayan-medium
```

Voices are automatically saved to `~/.local/share/piper-voices/`.

### 2. Alternative: Manual Download via HuggingFace

If the automatic download doesn't work, download manually:

```bash
# Create directory for voices
mkdir -p ~/.local/share/piper-voices
cd ~/.local/share/piper-voices

# Download model files from HuggingFace
# Format: https://huggingface.co/rhasspy/piper-voices/resolve/main/[lang]/[region]/[name]/[quality]/

# English voices
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx{,.json}
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx{,.json}

# Vietnamese voice
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/vi/vi_VN/vais1000/medium/vi_VN-vais1000-medium.onnx{,.json}

# Chinese voice
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/zh/zh_CN/huayan/medium/zh_CN-huayan-medium.onnx{,.json}
```

### 3. Browse All Available Voices

Visit: https://huggingface.co/rhasspy/piper-voices/tree/main

Available languages include:
- **English**: en_US, en_GB
- **Chinese**: zh_CN (limited availability)
- **Vietnamese**: vi_VN (limited availability)
- **Spanish, French, German, Italian**, and many more

### 4. Test Voice with Python API

Quick test to verify a voice works:

```python
import wave
from piper.voice import PiperVoice

# Load a voice (will search in ~/.local/share/piper-voices)
voice = PiperVoice.load("~/.local/share/piper-voices/en_US-lessac-medium.onnx")

# Synthesize to WAV file
with wave.open("test.wav", "wb") as wav_file:
    voice.synthesize_wav("Welcome to the world of speech synthesis!", wav_file)

print("✓ Test audio created: test.wav")
```

### 5. Advanced Synthesis Options

Adjust speech parameters:

```python
from piper.voice import PiperVoice, SynthesisConfig

voice = PiperVoice.load("/path/to/voice.onnx")

syn_config = SynthesisConfig(
    volume=0.5,        # Half as loud
    length_scale=2.0,  # Twice as slow
    noise_scale=1.0,   # More audio variation
    noise_w_scale=1.0, # More speaking variation
    normalize_audio=False  # Use raw audio from voice
)

voice.synthesize_wav("text", wav_file, syn_config=syn_config)
```

### 6. GPU Acceleration (Optional)

For faster synthesis with CUDA GPU:

```bash
pip install onnxruntime-gpu
```

```python
voice = PiperVoice.load("/path/to/voice.onnx", use_cuda=True)
```

## Recommended Voices for This Project

### Required for Chinese/Vietnamese Novel Processing

**Using automatic download (recommended):**
```bash
source .venv/bin/activate

# Vietnamese voices (primary)
python3 -m piper.download_voices vi_VN-vais1000-medium
python3 -m piper.download_voices vi_VN-vivos-x_low

# Chinese voices
python3 -m piper.download_voices zh_CN-huayan-medium

# English fallback
python3 -m piper.download_voices en_US-lessac-medium
python3 -m piper.download_voices en_US-amy-medium
```

**Manual download (if automatic fails):**
```bash
cd ~/.local/share/piper-voices

# Vietnamese
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/vi/vi_VN/vais1000/medium/vi_VN-vais1000-medium.onnx{,.json}
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/vi/vi_VN/vivos/x_low/vi_VN-vivos-x_low.onnx{,.json}

# Chinese
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/zh/zh_CN/huayan/medium/zh_CN-huayan-medium.onnx{,.json}

# English
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx{,.json}
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx{,.json}
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

**Solution**: Download the voice model:
```bash
python3 -m piper.download_voices en_US-lessac-medium
```

Or check if it exists:
```bash
ls ~/.local/share/piper-voices/*.onnx
```

### Download Command Fails

If `python3 -m piper.download_voices` doesn't work, use manual wget method (see section 2 above).

### Permission Errors
```bash
# Make sure directory is writable
mkdir -p ~/.local/share/piper-voices
chmod -R 755 ~/.local/share/piper-voices
```

### Test Voice in Python
```python
import wave
from piper.voice import PiperVoice

try:
    voice = PiperVoice.load("~/.local/share/piper-voices/en_US-lessac-medium.onnx")
    with wave.open("test.wav", "wb") as wav_file:
        voice.synthesize_wav("Hello world", wav_file)
    print("✓ Voice works!")
except Exception as e:
    print(f"✗ Error: {e}")
```

## Using OpenAI TTS Instead

If Piper setup is too complex, use OpenAI TTS (simpler, but requires API key):

```bash
export OPENAI_API_KEY="sk-..."
python tests/test_tts_synthesis.py openai
```

No voice models needed - works immediately with internet connection.
