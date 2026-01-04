# learn_language_through_novel — Quick Task Runner

This repository contains a small FastAPI service (`src/main.py`) that analyzes Chinese chapters and produces scene/sentence metadata and Vietnamese translations.

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
   python scripts/generate.py tasks/task1.json
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