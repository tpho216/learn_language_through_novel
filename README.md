# learn_language_through_novel — Quick Task Runner

This repository contains a small FastAPI service (`src/main.py`) that analyzes Chinese chapters and produces scene/sentence metadata and Vietnamese translations.

## Prerequisites

- **Python 3.12** (required for optimal compatibility)
- `python3.12-venv` package (for Ubuntu/Debian) or equivalent for your OS
- `pip` (usually included with Python)

> **Recommended Setup**: This project is developed and tested on **Ubuntu WSL with pyenv**. If you're using pyenv, see the pyenv-specific setup instructions below.

## Setup Virtual Environment

### Option A: Using pyenv (Recommended for Ubuntu WSL)

If you're using pyenv (the maintainer's preferred setup):

```bash
# Install Python 3.12 via pyenv
pyenv install 3.12

# Set Python 3.12 for this project
pyenv local 3.12

# Verify version
python --version  # Should show Python 3.12.x

# Create virtual environment
python -m venv .venv

# Activate
source .venv/bin/activate
```

### Option B: Using system Python

```bash
# Create virtual environment with Python 3.12
python3.12 -m venv .venv

# Activate on Linux/macOS
source .venv/bin/activate

# Activate on Windows
.venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

### 3. Install Piper TTS (Python API)

Piper is included in requirements.txt, but you may need system dependencies:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y libsndfile1

# macOS (with Homebrew)
brew install libsndfile

# Verify piper installation
python -c "from piper.voice import PiperVoice; print('Piper OK')"
```

For detailed Piper voice model setup, see [docs/PIPER_SETUP.md](docs/PIPER_SETUP.md).

**Troubleshooting?** See [docs/SETUP_TROUBLESHOOTING.md](docs/SETUP_TROUBLESHOOTING.md) for common issues and solutions.

### 4. Configure Environment Variables (Optional)

Create a `.env` file in the project root:

```bash
# OpenAI API key (if using OpenAI TTS)
OPENAI_API_KEY=your_api_key_here

# Piper voice models directory
PIPER_DATA_DIR=~/.local/share/piper-voices
```

## Running a generation task (local)

A lightweight task runner is available at `scripts/generate.py`. It posts a chapter to the local API (`/llm/analyze_chapter`), optionally truncates the number of sentences, and writes the response to `outputs/`.

Task schema (example `tasks/task1.json`):

```json
{
  "name": "task1",
  "chapter_id": "1000",
  "chapter_zh_path": "chapters/1000_zh.txt",
  "chapter_vi_ref_path": "chapters/1000_vi.txt",  
  "max_sentences": 10,
  "api_url": "http://localhost:8000/llm/analyze_chapter",
  "output_dir": "outputs"
}
```

Usage:

1. Start the API server locally:

   ```bash
   uvicorn src.main:app --reload --port 8000
   ```

2. Run a task:

   ```bash
   python scripts/generate.py tasks/task1.jsonpython scripts/generate.py tasks/task1.json
   ```

This writes the result to `outputs/<task_name>_<timestamp>.json` and includes `_meta` information (timestamp, task name, chapter id). If `max_sentences` is set, the output will be truncated to that many sentences (scene order preserved).

## Test runner helper (optional)

There is a helper script `scripts/run_task_with_server.sh` that starts a temporary local API on a test port, runs a task against it, and then stops the server. Example:

```bash
./scripts/run_task_with_server.sh tasks/task1.json 8001 20  # task, port, timeout-seconds
```
It patches the task's `api_url` to the local port, writes the output to `outputs/`, and cleans up the server process afterward.

---

If you'd like, I can add a short Makefile target or a GitHub Actions workflow to run tasks and collect outputs automatically. Let me know which you prefer.