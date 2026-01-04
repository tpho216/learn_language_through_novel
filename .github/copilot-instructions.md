# Copilot / AI Agent Instructions — learn_language_through_novel 🚀

## Short project summary
- This is a small FastAPI service that implements an **LLM + Piper (TTS)** pipeline for converting novel chapters into scene/sentence metadata and (eventually) audio assets.
- Main entry point: `main.py` (FastAPI app). No existing agent docs or README; add changes here or create `services/` modules for new logic.

## Quick start / dev workflow 🔧
- Install deps: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Run server locally: `uvicorn main:app --reload --port 8000`
- Endpoint to exercise: `POST /llm/analyze_chapter`

## Key files / places to change ⚠️
- `main.py` — app, Pydantic models and the `analyze_chapter` handler (core pipeline entry point).
- `audio/` — intended for produced audio assets (currently empty).
- `requirements.txt` — pinned dependencies (FastAPI, Pydantic v2, uvicorn, etc.).

## Data models & expectations (exact shapes) 📦
- Request: `AnalyzeChapterRequest`
  - `chapter_id: str`
  - `text_zh: str` (Chinese source text)
  - `text_vi_ref: Optional[str]` (Vietnamese reference translation provided by human translators; optional)

- Response: `AnalyzeChapterResponse` → `scenes: List[SceneMeta]`
  - Each `Sentence` now includes:
    - `text_vi_ref`: the human-supplied reference (may be `null`)
    - `text_vi_ai`: the AI-produced translation from Chinese
    - `text_vi`: the merged translation (prefer human `text_vi_ref` when valid, else use `text_vi_ai`)

- Response: `AnalyzeChapterResponse` → `scenes: List[SceneMeta]`
  - `SceneMeta`: `scene_id: str`, `description: str`, `sentences: List[SentenceMeta]`
  - `SentenceMeta`: `order: int`, `text_zh: str`, `character: str`, `voice: str`
    - NOTE: `voice` currently uses the values `narrator | male | female` in placeholder data.

## Concrete LLM work items (copyable instructions) 💡
When replacing the placeholder in `analyze_chapter` implement the following deterministic steps:
1. Feed the full chapter (`text_zh`) to the LLM.
2. Ask the LLM to:
   - Identify characters (names) appearing in the chapter.
   - Split the chapter into sentences (preserve order) and map each sentence to the speaking character or `narrator`.
   - For each sentence decide a `voice` value from `narrator|male|female` (project currently expects these values).
   - Produce JSON conforming exactly to `AnalyzeChapterResponse` (with `scene_id`, `description`, `sentences`).

Example request body:
```json
{
  "chapter_id": "chp-001",
  "text_zh": "韩立缓缓站起身来..."
}
```
Example minimal response (matches `main.py` placeholder):
```json
{
  "chapter_id": "chp-001",
  "scenes": [
    {
      "scene_id": "scene-001",
      "description": "Hàn Lập thi pháp",
      "sentences": [
        {"order":1, "text_zh":"韩立缓缓站起身来...", "character":"narrator", "voice":"narrator"}
      ]
    }
  ]
}
```

## Integration points to implement / where to plug services 🔗
- LLM: implement a small `services/llm.py` or `llm_client()` that accepts prompt + text and returns structured JSON. Keep the FastAPI route async and validate output against the Pydantic models.
- TTS / Piper: audio generation is expected but not present — write a `services/tts.py` that takes `SentenceMeta` and produces files under `audio/`.

## Conventions & constraints to preserve ✅
- Use Pydantic v2 models as in `main.py` and keep `response_model=` on route definitions to enforce shape.
- Keep async FastAPI endpoints.
- Preserve the semantic meaning of `character` and the three `voice` categories.
- When adding code, prefer small, focused modules and keep the HTTP contract stable (don't change request/response fields without a migration plan).

## Testing & debugging notes 🐞
- There are no tests currently. For quick validation, run the server and use `curl` or an HTTP client (e.g., httpx) to call `/llm/analyze_chapter` and verify Pydantic validation.
- Use `uvicorn --reload` to catch code changes fast.

---

If any of these sections are unclear or you'd like me to expand with concrete PR tasks, tests examples, or a suggested `services/` layout, tell me which part to iterate on. ✨
