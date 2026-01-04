#!/usr/bin/env python3
"""End-to-end test: analyze → enrich → prepare TTS → synthesize → merge."""

import httpx
import json
import sys
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.utils.audio import concatenate_wav_files


BASE_URL = "http://localhost:8000"


def test_e2e_pipeline():
    """Test complete pipeline from text to merged audio."""
    
    print("=" * 60)
    print("END-TO-END TEST: Full TTS Pipeline")
    print("=" * 60)
    
    # Sample Chinese text
    text_zh = "你好，世界。这是一个测试。"
    chapter_id = "test_e2e"
    
    # Step 1: Analyze chapter
    print("\n[1/5] Analyzing chapter...")
    analyze_payload = {
        "chapter_id": chapter_id,
        "text_zh": text_zh,
        "text_vi_ref": None
    }
    
    try:
        resp = httpx.post(f"{BASE_URL}/llm/analyze_chapter", json=analyze_payload, timeout=60.0)
        if resp.status_code != 200:
            print(f"✗ Analysis failed: {resp.status_code} {resp.text}")
            return 1
        
        analysis = resp.json()
        print(f"✓ Analyzed: {len(analysis['scenes'])} scenes")
        
        # Get first sentence
        if not analysis['scenes'] or not analysis['scenes'][0]['sentences']:
            print("✗ No sentences found")
            return 1
        
        sentence = analysis['scenes'][0]['sentences'][0]
        print(f"  Sentence: {sentence['text_zh'][:50]}...")
        
    except Exception as e:
        print(f"✗ Analysis error: {e}")
        return 1
    
    # Step 2: Enrich sentence
    print("\n[2/5] Enriching sentence...")
    enrich_payload = {
        "chapter_id": chapter_id,
        "sentence": {
            "order": sentence['order'],
            "text_zh": sentence['text_zh'],
            "text_vi": sentence.get('text_vi')
        }
    }
    
    try:
        resp = httpx.post(f"{BASE_URL}/llm/enrich_sentence", json=enrich_payload, timeout=60.0)
        if resp.status_code != 200:
            print(f"✗ Enrichment failed: {resp.status_code} {resp.text}")
            return 1
        
        enrichment = resp.json()
        print(f"✓ Enriched: {len(enrichment['phrases'])} phrases, {len(enrichment['examples'])} examples")
        
    except Exception as e:
        print(f"✗ Enrichment error: {e}")
        return 1
    
    # Step 3: Prepare TTS segments
    print("\n[3/5] Preparing TTS segments...")
    tts_prep_payload = {
        "enriched_sentence": enrichment,
        "chapter_title_zh": "测试章节",
        "chapter_title_vi": "Chương thử nghiệm",
        "selection": [
            "title.zh",
            "title.vi",
            "sentence.text_zh",
            "phrases[].text",
            "phrases[].meaning_vi"
        ],
        "lang_cues": {
            "zh": "中文",
            "vi": "Tiếng Việt"
        },
        "field_cues": {
            "title.zh": {"zh": "标题"},
            "title.vi": {"vi": "Tựa đề"},
            "sentence.text_zh": {"zh": "原文"},
            "phrases[].text": {"zh": "词汇"},
            "phrases[].meaning_vi": {"vi": "Nghĩa"}
        }
    }
    
    try:
        resp = httpx.post(f"{BASE_URL}/llm/prepare_tts_segments", json=tts_prep_payload, timeout=30.0)
        if resp.status_code != 200:
            print(f"✗ TTS prep failed: {resp.status_code} {resp.text}")
            return 1
        
        tts_segments_resp = resp.json()
        segments = tts_segments_resp['segments']
        print(f"✓ Prepared {len(segments)} TTS segments")
        
    except Exception as e:
        print(f"✗ TTS prep error: {e}")
        return 1
    
    # Step 4: Synthesize audio
    print("\n[4/5] Synthesizing audio...")
    output_dir = Path("outputs/audio/test_e2e")
    
    synthesis_payload = {
        "segments": segments,
        "output_dir": str(output_dir),
        "provider": "piper",
        "filename_prefix": "e2e_seg"
    }
    
    try:
        resp = httpx.post(f"{BASE_URL}/tts/synthesize", json=synthesis_payload, timeout=120.0)
        if resp.status_code != 200:
            print(f"✗ Synthesis failed: {resp.status_code} {resp.text}")
            return 1
        
        synthesis_result = resp.json()
        print(f"✓ Synthesized {synthesis_result['successful']}/{synthesis_result['total_segments']} segments")
        
        if synthesis_result['failed'] > 0:
            print("  Failed segments:")
            for r in synthesis_result['results']:
                if not r['success']:
                    print(f"    - Segment {r['order']}: {r.get('error', 'Unknown error')}")
        
        # Collect successful audio files
        audio_files = [
            Path(r['output_path'])
            for r in synthesis_result['results']
            if r['success']
        ]
        
        if not audio_files:
            print("✗ No audio files generated")
            return 1
        
        print(f"  Audio files: {[f.name for f in audio_files]}")
        
    except Exception as e:
        print(f"✗ Synthesis error: {e}")
        return 1
    
    # Step 5: Merge audio files
    print("\n[5/5] Merging audio segments...")
    merged_file = output_dir / "e2e_merged.wav"
    
    try:
        audio_files.sort()  # Ensure correct order
        
        merge_result = concatenate_wav_files(
            audio_files,
            merged_file,
            silence_ms=500  # 500ms pause between segments
        )
        
        print(f"✓ Merged {merge_result['total_segments']} segments")
        print(f"  Output: {merged_file}")
        print(f"  Duration: {merge_result['duration_seconds']}s")
        print(f"  Sample rate: {merge_result['sample_rate']} Hz")
        
    except Exception as e:
        print(f"✗ Merge error: {e}")
        return 1
    
    # Summary
    print("\n" + "=" * 60)
    print("✓ END-TO-END TEST PASSED")
    print("=" * 60)
    print(f"Merged audio file: {merged_file}")
    print(f"Total segments: {len(audio_files)}")
    print(f"Total duration: {merge_result['duration_seconds']}s")
    print()
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(test_e2e_pipeline())
    except KeyboardInterrupt:
        print("\n✗ Test interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
