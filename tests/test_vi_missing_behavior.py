import json
from types import SimpleNamespace
from fastapi.testclient import TestClient
import os

from main import app

client = TestClient(app)


class FakeOpenAIResponse:
    def __init__(self, content):
        self.choices = [SimpleNamespace(message=SimpleNamespace(content=content))]


class FakeOpenAI:
    def __init__(self, api_key=None):
        pass

    class chat:
        class completions:
            @staticmethod
            def create(*args, **kwargs):
                # This will be monkeypatched per-test by setting FakeOpenAI._response_content
                return FakeOpenAI._response


def make_fake_resp_no_vi(chapter_id="1000"):
    # Sentence with no text_vi fields
    resp = {
        "chapter_id": chapter_id,
        "scenes": [
            {
                "scene_id": "s1",
                "description": "d",
                "sentences": [
                    {"order": 1, "text_zh": "测试句子。"}
                ]
            }
        ]
    }
    return json.dumps(resp)


def make_fake_resp_partial_vi(chapter_id="1000"):
    # Sentence with only text_vi_ai (missing ref)
    resp = {
        "chapter_id": chapter_id,
        "scenes": [
            {
                "scene_id": "s1",
                "description": "d",
                "sentences": [
                    {"order": 1, "text_zh": "测试句子。", "text_vi_ai": "Câu thử nghiệm."}
                ]
            }
        ]
    }
    return json.dumps(resp)


def test_hard_failure_when_no_vi_fields(monkeypatch):
    # Ensure env var is set so code doesn't raise earlier
    monkeypatch.setenv("OPENAI_API_KEY", "fake")

    # Monkeypatch OpenAI in the main module to our FakeOpenAI configured to return no-vi
    fake = FakeOpenAI()
    FakeOpenAI._response = FakeOpenAIResponse(make_fake_resp_no_vi())
    monkeypatch.setattr("main.OpenAI", lambda api_key=None: fake)

    payload = {"chapter_id": "1000", "text_zh": "测试句子。"}
    r = client.post("/llm/analyze_chapter", json=payload)
    assert r.status_code == 502
    detail = r.json().get("detail", {})
    assert detail.get("error") == "LLM_MISSING_VI"
    assert detail.get("chapter_id") == "1000"


def test_logs_when_partial_missing(monkeypatch, caplog):
    monkeypatch.setenv("OPENAI_API_KEY", "fake")
    fake = FakeOpenAI()
    FakeOpenAI._response = FakeOpenAIResponse(make_fake_resp_partial_vi())
    monkeypatch.setattr("main.OpenAI", lambda api_key=None: fake)

    caplog.clear()
    caplog.set_level("WARNING")

    payload = {"chapter_id": "1000", "text_zh": "测试句子。"}
    r = client.post("/llm/analyze_chapter", json=payload)
    assert r.status_code == 200

    # There should be a warning logged about missing fields (text_vi_ref missing)
    found = any("Missing vi fields" in rec.message or "Missing vi fields" in rec.getMessage() for rec in caplog.records)
    assert found
