# Setup Troubleshooting Guide

Common issues and solutions when setting up the development environment.

> **Note**: This project is maintained on **Ubuntu WSL with pyenv**. The pyenv setup is recommended for the best experience.

---

## Python 3.12 Installation

### Using pyenv (Recommended for Ubuntu WSL)

Pyenv allows you to easily manage multiple Python versions. This is the maintainer's preferred setup.

#### Install pyenv on Ubuntu WSL

```bash
# Install dependencies
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
  libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
  libffi-dev liblzma-dev

# Install pyenv
curl https://pyenv.run | bash

# Add to ~/.bashrc (or ~/.zshrc)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# Reload shell
exec $SHELL

# Verify installation
pyenv --version
```

#### Install Python 3.12 with pyenv

```bash
# Install Python 3.12 (latest patch version)
pyenv install 3.12

# Set as local version for this project
cd /path/to/learn_language_through_novel
pyenv local 3.12

# Verify
python --version  # Should show Python 3.12.x
which python      # Should point to pyenv shims
```

#### Create venv with pyenv

```bash
# Now create venv as normal
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
py
---

## Piper TTS Installation Issues

### Issue: `ModuleNotFoundError: No module named 'piper'`

**Solution**: Ensure you're in the activated venv and piper-tts is installed:
```bash
source .venv/bin/activate
pip install piper-tts==1.2.0
```

### Issue: `OSError: libsndfile.so.1: cannot open shared object file`

**Solution**: Install system audio libraries:

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install -y libsndfile1
```

**macOS**:
```bash
brew install libsndfile
```

### Issue: `ImportError: cannot import name 'PiperVoice' from 'piper'`

**Solution**: There might be a package conflict. Uninstall and reinstall:
```bash
pip uninstall piper piper-tts -y
pip install piper-tts==1.2.0
```

### Issue: Piper works but no voice models found

**Solution**: Download voice models (see [PIPER_SETUP.md](PIPER_SETUP.md)):
```bash
mkdir -p ~/.local/share/piper-voices
cd ~/.local/share/piper-voices
# Download a sample voice
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
```

---

## Dependency Installation Issues

### Issue: `pip` command not found after activating venv

**Solution**: Use python's module invocation:
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Issue: Slow package installation

**Solution**: Use a faster mirror (optional):
```bash
pip install -r requirements.txt -i https://pypi.org/simple
```

### Issue: Incompatible dependency versions

**Solution**: Ensure you're using Python 3.12 and reinstall all packages:
```bash
python --version  # Must be 3.12.x
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

---

## ONNX Runtime Issues

### Issue: `onnxruntime` installation fails on ARM architecture (M1/M2 Mac)

**Solution**: Use the correct wheel for Apple Silicon:
```bash
pip uninstall onnxruntime
pip install onnxruntime-silicon  # For M1/M2 Macs
```

Or stay with the specified version which should work:
```bash
pip install onnxruntime==1.23.2
```

---

## Environment Variables

### Issue: `.env` file not being loaded

**Solution**: Ensure you have `python-dotenv` installed (already in requirements.txt) and your code loads it:

```python
from dotenv import load_dotenv
load_dotenv()
```

For debugging, verify the file is being read:
```bash
cat .env
```

---

## Testing Your Setup

After resolving issues, verify everything works:

```bash
# Activate venv
source .venv/bin/activate

# Check Python version
python --version  # Should be 3.12.x

# Test imports
python -c "import fastapi; import pydantic; print('FastAPI OK')"
python -c "from piper.voice import PiperVoice; print('Piper OK')"

# Run tests
python -m pytest tests/ -v

# Start server
uvicorn src.main:app --reload --port 8000
```

---

## Still Having Issues?

1. Check your Python version: `python --version`
2. Verify you're in the venv: `which python` (should point to `.venv/bin/python`)
3. Check installed packages: `pip list`
4. Review logs for specific error messages
5. Open an issue on GitHub with:
   - Your OS and version
   - Python version (`python --version`)
   - Full error traceback
   - Output of `pip list`
