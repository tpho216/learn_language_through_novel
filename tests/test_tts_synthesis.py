#!/usr/bin/env python3
"""Test TTS synthesis with a simple example."""

import httpx
import json
import sys

# Sample TTS segments
SAMPLE_SEGMENTS = [
    {
        "order": 1,
        "lang": "zh",
        "voice": "narrator",
        "style": "neutral",
        "text": "你好，世界",
        "pause_after_ms": 500
    },
    {
        "order": 2,
        "lang": "vi",
        "voice": "teacher",
        "style": "explanatory",
        "text": "Xin chào, thế giới",
        "pause_after_ms": 500
    },
    {
        "order": 3,
        "lang": "en",
        "voice": "narrator",
        "style": "neutral",
        "text": "Hello, world",
        "pause_after_ms": 500
    }
]


def test_synthesis(provider: str = "piper", base_url: str = "http://localhost:8000"):
    """Test TTS synthesis endpoint."""
    
    url = f"{base_url}/tts/synthesize"
    
    payload = {
        "segments": SAMPLE_SEGMENTS,
        "output_dir": "outputs/audio",
        "provider": provider,
        "filename_prefix": f"test_{provider}"
    }
    
    if provider == "openai":
        payload["openai_model"] = "standard"
    
    print(f"Testing TTS synthesis with provider: {provider}")
    print(f"Endpoint: {url}")
    print(f"Segments: {len(SAMPLE_SEGMENTS)}")
    print()
    
    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                print("✓ Synthesis completed successfully!")
                print(f"  Total: {result['total_segments']}")
                print(f"  Successful: {result['successful']}")
                print(f"  Failed: {result['failed']}")
                print(f"  Output dir: {result['output_dir']}")
                print()
                
                # Show individual results
                for res in result['results']:
                    if res['success']:
                        print(f"  ✓ Segment {res['order']}: {res['output_path']} ({res.get('duration_seconds', 'N/A')}s)")
                    else:
                        print(f"  ✗ Segment {res['order']}: {res.get('error', 'Unknown error')}")
                
                return 0
            else:
                print(f"✗ Error: {response.status_code}")
                print(response.text)
                return 1
                
    except httpx.ConnectError:
        print("✗ Connection failed. Is the server running?")
        print(f"  Start server with: uvicorn src.main:app --reload --port 8000")
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    provider = sys.argv[1] if len(sys.argv) > 1 else "piper"
    if provider not in ["piper", "openai"]:
        print(f"Usage: {sys.argv[0]} [piper|openai]")
        sys.exit(1)
    
    sys.exit(test_synthesis(provider))
