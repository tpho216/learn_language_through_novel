"""Simple task runner for /llm/analyze_chapter.

Usage:
  python scripts/generate.py tasks/task1.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, List
import sys

import httpx
import re

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.utils.audio import concatenate_wav_files

# =========================
# Sentence splitting / truncation (TEST MODE)
# =========================

ZH_SENTENCE_RE = re.compile(r"(?<=[。！？])")
VI_SENTENCE_RE = re.compile(r"(?<=[.!?])")


def split_sentences(text: str, lang: str) -> List[str]:
    if not text:
        return []
    if lang == "zh":
        return [s.strip() for s in ZH_SENTENCE_RE.split(text) if s.strip()]
    else:
        return [s.strip() for s in VI_SENTENCE_RE.split(text) if s.strip()]


def truncate_request_texts(
    text_zh: str,
    text_vi: Optional[str],
    max_sentences: Optional[int],
) -> Tuple[str, Optional[str]]:
    if not max_sentences or max_sentences <= 0:
        return text_zh, text_vi

    zh_sents = split_sentences(text_zh, "zh")
    zh_cut = zh_sents[:max_sentences]

    vi_cut = None
    if text_vi:
        vi_sents = split_sentences(text_vi, "vi")
        vi_cut = vi_sents[:len(zh_cut)]

    return (
        "".join(zh_cut),
        "".join(vi_cut) if vi_cut else None,
    )


# =========================
# Task helpers
# =========================

def load_task(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def read_text(path: Optional[Path]) -> Optional[str]:
    if not path or not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def enrich_sentence(
    api_url: str,
    chapter_id: str,
    sentence: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Call the /llm/enrich_sentence endpoint for a single sentence."""
    payload = {
        "chapter_id": chapter_id,
        "sentence": {
            "order": sentence.get("order"),
            "text_zh": sentence.get("text_zh"),
            "text_vi": sentence.get("text_vi"),
        },
    }

    try:
        resp = httpx.post(api_url, json=payload, timeout=30.0)
        if resp.status_code != 200:
            print(f"⚠️ Enrich failed for sentence {sentence.get('order')}: {resp.text}")
            return None
        return resp.json()
    except Exception as e:
        print(f"⚠️ Enrich exception for sentence {sentence.get('order')}: {e}")
        return None


async def enrich_sentences_parallel(
    api_url: str,
    chapter_id: str,
    sentences: List[Dict[str, Any]],
    max_concurrent: int = 3,
) -> Dict[int, Optional[Dict[str, Any]]]:
    """Enrich multiple sentences in parallel with concurrency limit."""
    results: Dict[int, Optional[Dict[str, Any]]] = {}

    async def enrich_one(client: httpx.AsyncClient, sentence: Dict[str, Any]) -> None:
        order = sentence.get("order")
        payload = {
            "chapter_id": chapter_id,
            "sentence": {
                "order": order,
                "text_zh": sentence.get("text_zh"),
                "text_vi": sentence.get("text_vi"),
                "text_vi_ref": sentence.get("text_vi_ref"),
            },
        }

        max_attempts = 3
        base_delay = 2

        for attempt in range(1, max_attempts + 1):
            try:
                resp = await client.post(api_url, json=payload, timeout=180.0)  # Increased to 3 minutes for complex enrichment
                if resp.status_code != 200:
                    print(f"⚠️ Enrich failed for sentence {order}: {resp.text}")
                    results[order] = None
                    return

                results[order] = resp.json()
                return

            except httpx.ReadTimeout as e:
                if attempt < max_attempts:
                    delay = base_delay * (2 ** (attempt - 1))
                    print(
                        f"⏳ Timeout on sentence {order} (attempt {attempt}/{max_attempts}); retrying in {delay}s"
                    )
                    await asyncio.sleep(delay)
                    continue
                print(f"⚠️ Enrich timeout for sentence {order}: {e}\n{traceback.format_exc()}")
                results[order] = None
                return

            except Exception as e:
                print(f"⚠️ Enrich exception for sentence {order}: {e}\n{traceback.format_exc()}")
                results[order] = None
                return

    async with httpx.AsyncClient() as client:
        # Use semaphore to limit concurrency
        semaphore = asyncio.Semaphore(max_concurrent)

        async def bounded_enrich(s: Dict[str, Any]) -> None:
            async with semaphore:
                await enrich_one(client, s)

        tasks = [bounded_enrich(s) for s in sentences]
        await asyncio.gather(*tasks)

    return results


# =========================
# Main runner
# =========================

def run(task_path: Path) -> int:
    task = load_task(task_path)

    name = task.get("name") or task_path.stem
    chapter_id = task.get("chapter_id")
    if not chapter_id:
        print("task must include 'chapter_id'")
        return 2

    zh_path = Path(task.get("chapter_zh_path", ""))
    vi_ref_path = Path(task.get("chapter_vi_ref_path", "")) if task.get("chapter_vi_ref_path") else None
    max_sentences = task.get("max_sentences")  # ✅ NEW
    api_url = task.get("api_url", "http://localhost:8000/llm/analyze_chapter")
    output_dir = Path(task.get("output_dir", "outputs"))

    if not zh_path.exists():
        print(f"Chinese chapter file not found: {zh_path}")
        return 2

    # ---- read raw texts
    raw_text_zh = read_text(zh_path) or ""
    raw_text_vi = read_text(vi_ref_path) if vi_ref_path else None

    # ---- truncate (TEST MODE)
    text_zh, text_vi_ref = truncate_request_texts(
        raw_text_zh,
        raw_text_vi,
        max_sentences,
    )


    print(f"Read {len(raw_text_zh)} chars (zh), truncated to {len(text_zh)}")
    if raw_text_vi:
        print(f"Read {len(raw_text_vi)} chars (vi), truncated to {len(text_vi_ref) if text_vi_ref else 0}")
    else:
        print("No Vietnamese reference text provided.")

    print("Preparing payload...")
    payload: Dict[str, Any] = {
        "chapter_id": chapter_id,
        "text_zh": text_zh,
    }
    if text_vi_ref:
        payload["text_vi_ref"] = text_vi_ref

    print("Payload prepared., payload contents: ", payload)
    print(f"Posting to {api_url} (chapter_id={chapter_id}, max_sentences={max_sentences})...")

    try:
        resp = httpx.post(api_url, json=payload, timeout=60.0)
    except Exception as e:
        print(f"Error posting to API: {e}")
        return 3

    if resp.status_code != 200:
        try:
            err = resp.json()
        except Exception:
            err = resp.text
        print(f"API returned status {resp.status_code}: {err}")
        return 4

    out = resp.json()

    # =========================
    # Optional sentence enrichment
    # =========================
    enable_enrichment = task.get("enable_enrichment", False)
    enrich_api_url = task.get("enrich_api_url")
    enrich_max_concurrent = task.get("enrich_max_concurrent", 3)
    max_enrich_sentences = task.get("max_enrich_sentences", 1)

    if enable_enrichment:
        if not enrich_api_url:
            print("⚠️ enable_enrichment=true but enrich_api_url not set")
        else:
            # Collect all sentences from all scenes
            all_sentences = []
            scene_sentence_map = []  # Track which scene/index each sentence belongs to
            for scene_idx, scene in enumerate(out.get("scenes", [])):
                for sent_idx, s in enumerate(scene.get("sentences", [])):
                    all_sentences.append(s)
                    scene_sentence_map.append((scene_idx, sent_idx))

            # Limit enrichment to max_enrich_sentences
            sentences_to_enrich = all_sentences[:max_enrich_sentences]
            map_to_enrich = scene_sentence_map[:max_enrich_sentences]

            print(f"🔍 Enriching {len(sentences_to_enrich)}/{len(all_sentences)} sentences (max {enrich_max_concurrent} concurrent)...")

            # Enrich in parallel
            enrichments = asyncio.run(
                enrich_sentences_parallel(
                    enrich_api_url,
                    chapter_id,
                    sentences_to_enrich,
                    max_concurrent=enrich_max_concurrent,
                )
            )

            # Attach enrichments back to sentences
            for i, (scene_idx, sent_idx) in enumerate(map_to_enrich):
                sentence = out["scenes"][scene_idx]["sentences"][sent_idx]
                order = sentence.get("order")
                if order in enrichments and enrichments[order]:
                    sentence["enrichment"] = enrichments[order]

            # Attach enrichments back to sentences
            for i, (scene_idx, sent_idx) in enumerate(scene_sentence_map):
                sentence = out["scenes"][scene_idx]["sentences"][sent_idx]
                order = sentence.get("order")
                if order in enrichments and enrichments[order]:
                    sentence["enrichment"] = enrichments[order]

    # =========================
    # Optional TTS segment preparation
    # =========================
    prepare_tts_enabled = task.get("prepare_tts_segments", False)
    tts_api_url = task.get("tts_api_url")
    tts_selection = task.get("tts_selection")
    tts_lang_cues = task.get("tts_lang_cues")
    tts_field_cues = task.get("tts_field_cues")

    if prepare_tts_enabled:
        if not tts_api_url:
            print("⚠️ prepare_tts_segments=true but tts_api_url not set")
        else:
            print(f"📢 Preparing TTS segments for enriched sentences (deterministic)...")
            out.setdefault("tts_segments", [])

            chapter_title_zh = out.get("chapter_meta", {}).get("title")
            chapter_title_vi = None
            chapter_meta = out.get("chapter_meta", {})
            if chapter_meta.get("title_vi_ref"):
                chapter_title_vi = chapter_meta.get("title_vi_ref")
            elif chapter_meta.get("title_vi_ai"):
                chapter_title_vi = chapter_meta.get("title_vi_ai")

            # Track order counter across all sentences to avoid duplicates
            next_order = 1
            
            for scene in out.get("scenes", []):
                for sentence in scene.get("sentences", []):
                    if "enrichment" in sentence:
                        order = sentence.get("order")
                        enrichment = sentence["enrichment"]

                        payload = {
                            "enriched_sentence": dict(enrichment),
                            "chapter_title_zh": chapter_title_zh,
                            "chapter_title_vi": chapter_title_vi,
                            "start_order": next_order,  # Continue from last segment
                        }
                        # Carry sentence-level translations to TTS payload so they can be segmented
                        if sentence.get("text_vi"):
                            payload["enriched_sentence"]["text_vi"] = sentence.get("text_vi")
                        if sentence.get("text_vi_ref"):
                            payload["enriched_sentence"]["text_vi_ref"] = sentence.get("text_vi_ref")
                        if sentence.get("text_vi_ai"):
                            payload["enriched_sentence"]["text_vi_ai"] = sentence.get("text_vi_ai")
                        if tts_selection:
                            payload["selection"] = tts_selection
                        if tts_lang_cues:
                            payload["lang_cues"] = tts_lang_cues
                        if tts_field_cues:
                            payload["field_cues"] = tts_field_cues

                        try:
                            resp = httpx.post(tts_api_url, json=payload, timeout=300.0)
                            if resp.status_code != 200:
                                print(f"⚠️ TTS preparation failed for sentence {order}: {resp.text}")
                            else:
                                tts_data = resp.json()
                                segments = tts_data.get("segments", [])
                                out["tts_segments"].extend(segments)
                                # Update next_order to continue from where we left off
                                if segments:
                                    next_order = max(seg["order"] for seg in segments) + 1
                                print(f"✓ TTS segments generated for sentence {order}")
                        except Exception as e:
                            print(f"⚠️ TTS exception for sentence {order}: {e}")

    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    out_path = output_dir / f"{name}_{timestamp}.json"

    out.setdefault("_meta", {}).update({
        "timestamp": timestamp,
        "task": name,
        "chapter_id": chapter_id,
        "max_sentences": max_sentences,
    })

    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    scenes = out.get("scenes", [])
    sentence_count = sum(len(s.get("sentences", [])) for s in scenes)

    # =========================
    # Synthesize audio if enabled
    # =========================
    if task.get("synthesize_audio") and "tts_segments" in out:
        print("\n=== Synthesizing Audio ===")
        synthesis_api = task.get("synthesis_api_url", "http://localhost:8000/tts/synthesize")
        provider = task.get("synthesis_provider", "piper")
        audio_dir = Path(task.get("synthesis_output_dir", "outputs/audio"))
        merge_segments = task.get("synthesis_merge_segments", False)
        
        segments = out["tts_segments"]
        print(f"Synthesizing {len(segments)} segments with provider: {provider}")
        
        synthesis_payload = {
            "segments": segments,
            "output_dir": str(audio_dir / name / timestamp),
            "provider": provider,
            "filename_prefix": f"{chapter_id}_seg"
        }
        
        try:
            resp = httpx.post(synthesis_api, json=synthesis_payload, timeout=120.0)
            if resp.status_code == 200:
                result = resp.json()
                print(f"✓ Synthesized {result['successful']}/{result['total_segments']} segments")
                print(f"  Output: {result['output_dir']}")
                
                # Show first few errors if any failed
                if result['failed'] > 0:
                    print(f"\n⚠️ {result['failed']} segments failed:")
                    failed_results = [r for r in result['results'] if not r['success']][:3]
                    for r in failed_results:
                        print(f"  - Segment {r['order']}: {r.get('error', 'Unknown error')}")
                    if result['failed'] > 3:
                        print(f"  ... and {result['failed'] - 3} more")
                
                # Merge segments into single file if enabled
                if merge_segments and result['successful'] > 0:
                    audio_files = [
                        Path(r['output_path']) 
                        for r in result['results'] 
                        if r['success']
                    ]
                    audio_files.sort()  # Ensure correct order
                    
                    merged_file = Path(result['output_dir']) / f"{chapter_id}_merged.wav"
                    print(f"Merging {len(audio_files)} segments into {merged_file}...")
                    
                    merge_result = concatenate_wav_files(
                        audio_files,
                        merged_file,
                        silence_ms=500  # 500ms pause between segments
                    )
                    print(f"✓ Merged audio: {merge_result['duration_seconds']}s")
                    out["_meta"]["merged_audio_file"] = str(merged_file)
                    out["_meta"]["merged_audio_duration"] = merge_result['duration_seconds']
                    
                    # Re-save JSON with audio metadata
                    with out_path.open("w", encoding="utf-8") as fh:
                        json.dump(out, fh, ensure_ascii=False, indent=2)
            else:
                print(f"✗ Synthesis failed: {resp.status_code} {resp.text}")
        except Exception as e:
            print(f"✗ Synthesis error: {e}")

    print(f"\nWrote {out_path} — scenes={len(scenes)} sentences={sentence_count}")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run a generation task against /llm/analyze_chapter")
    parser.add_argument("task", help="Path to task JSON file (e.g., tasks/task1.json)")
    args = parser.parse_args(argv)

    task_path = Path(args.task)
    if not task_path.exists():
        print(f"Task file not found: {task_path}")
        return 2

    return run(task_path)


if __name__ == "__main__":
    raise SystemExit(main())
