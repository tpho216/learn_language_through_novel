from pathlib import Path
from fastapi.testclient import TestClient
from main import app
import re

client = TestClient(app)


def _first_paragraph_from_file(path: Path) -> str:
    text = path.read_text(encoding="utf-8").strip()
    # split on blank lines
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return paras[0]


def test_first_paragraph_minimal_schema():
    chapter_path = Path(__file__).parent.parent / "chapters" / "1000_zh.txt"
    paragraph = _first_paragraph_from_file(chapter_path)
    chapter_id = chapter_path.stem.split("_")[0]

    payload = {"chapter_id": chapter_id, "text_zh": paragraph}
    r = client.post("/llm/analyze_chapter", json=payload)
    assert r.status_code == 200
    j = r.json()

    # Persist JSON response to tests/fixtures for easy inspection and print the path
    import json as _json
    fixtures_dir = Path(__file__).parent / "fixtures"
    fixtures_dir.mkdir(exist_ok=True)
    fixture_path = fixtures_dir / f"response_{chapter_id}.json"
    fixture_path.write_text(_json.dumps(j, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote JSON response to: {fixture_path}")

    # Minimal top-level shape
    assert "chapter_id" in j and isinstance(j["chapter_id"], str)
    assert "scenes" in j and isinstance(j["scenes"], list) and len(j["scenes"]) > 0

    scene = j["scenes"][0]
    assert "scene_id" in scene and isinstance(scene["scene_id"], str)
    assert "description" in scene and isinstance(scene["description"], str)
    assert "sentences" in scene and isinstance(scene["sentences"], list) and len(scene["sentences"]) > 0

    sent = scene["sentences"][0]
    # Required sentence fields per updated schema
    assert "order" in sent and isinstance(sent["order"], int)
    assert "text_zh" in sent and isinstance(sent["text_zh"], str)
    # Vietnamese translation may be provided as `text_vi` or `text_vi_ai` (AI-produced). Accept either.
    assert (("text_vi" in sent and isinstance(sent["text_vi"], str)) or ("text_vi_ai" in sent and isinstance(sent["text_vi_ai"], str)))
    assert "character" in sent and isinstance(sent["character"], str)
    # voice must be one of the allowed values
    assert "voice" in sent and sent["voice"] in {"narrator", "male", "female", "unknown"}
    # is_dialogue must be present and boolean
    assert "is_dialogue" in sent and isinstance(sent["is_dialogue"], bool)

    # Ensure the returned sentence contains (or is contained in) the paragraph (approximate check)
    short_fragment = paragraph[:40]
    assert short_fragment in sent["text_zh"] or sent["text_zh"] in paragraph


def test_first_paragraph_with_vi_ref():
    # When a Vietnamese reference is supplied, the API should include text_vi (AI) and text_vi_ref (the provided ref)
    chapter_path = Path(__file__).parent.parent / "chapters" / "1000_zh.txt"
    chapter_vi_path = Path(__file__).parent.parent / "chapters" / "1000_vi.txt"
    paragraph_zh = _first_paragraph_from_file(chapter_path)
    paragraph_vi = _first_paragraph_from_file(chapter_vi_path)
    chapter_id = chapter_path.stem.split("_")[0]

    payload = {"chapter_id": chapter_id, "text_zh": paragraph_zh, "text_vi_ref": paragraph_vi}
    r = client.post("/llm/analyze_chapter", json=payload)
    assert r.status_code == 200
    j = r.json()

    # Persist response so we can inspect it
    import json as _json
    fixtures_dir = Path(__file__).parent / "fixtures"
    fixtures_dir.mkdir(exist_ok=True)
    fixture_path = fixtures_dir / f"response_{chapter_id}_with_vi_ref.json"
    fixture_path.write_text(_json.dumps(j, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote JSON response to: {fixture_path}")

    scene = j["scenes"][0]
    sent = scene["sentences"][0]

    # The API should provide a merged Vietnamese translation as `text_vi` (non-empty string)
    assert "text_vi" in sent and isinstance(sent["text_vi"], str) and sent["text_vi"].strip() != ""
    # The provided Vietnamese ref should be attached as text_vi_ref (may be None)
    assert "text_vi_ref" in sent and isinstance(sent["text_vi_ref"], (str, type(None)))
    # If it's present it should include a fragment of the provided Vietnamese paragraph
    if sent["text_vi_ref"]:
        assert paragraph_vi[:40] in sent["text_vi_ref"] or sent["text_vi_ref"] in paragraph_vi


def test_no_title_detected_when_absent():
    client_local = TestClient(app)

    paragraph_zh = "这是一段没有标题的正文内容，用于测试当没有标题时不应返回标题。"
    payload = {"chapter_id": "no-title", "text_zh": paragraph_zh}

    r = client_local.post("/llm/analyze_chapter", json=payload)
    assert r.status_code == 200
    j = r.json()

    chapter_meta = j.get("chapter_meta", {})
    assert chapter_meta.get("title") is None
    assert chapter_meta.get("title_vi_ref") in (None, "")
    assert chapter_meta.get("title_vi_ai") in (None, "")

    # scenes should still be present
    assert j.get("scenes")
