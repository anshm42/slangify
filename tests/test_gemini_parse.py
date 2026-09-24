import asyncio
from types import SimpleNamespace

from slangify.sources import gemini
from slangify.sources.gemini import EXTRACT_PROMPT, SYSTEM_PROMPT, _parse_json_array


def test_prompts_exclude_non_slang_terms():
    for prompt in (SYSTEM_PROMPT, EXTRACT_PROMPT):
        assert "ordinary words" in prompt
        assert "When uncertain, exclude it." in prompt


def test_prompts_include_regional_slang():
    for prompt in (SYSTEM_PROMPT, EXTRACT_PROMPT):
        assert "regional and community-specific spoken slang" in prompt
        assert "`nize` is Toronto slang" in prompt


def test_falls_back_after_transient_gemini_error(monkeypatch):
    class TransientError(Exception):
        code = 503

    calls = []

    async def generate(model, system_prompt, text):
        calls.append(model)
        if model == "primary":
            raise TransientError()
        return SimpleNamespace(text="[]")

    monkeypatch.setattr(gemini, "MODEL", "primary")
    monkeypatch.setattr(gemini, "FALLBACK_MODEL", "fallback")
    monkeypatch.setattr(gemini, "_generate", generate)

    assert asyncio.run(gemini._call("prompt", "message")) == "[]"
    assert calls == ["primary", "fallback"]


def test_does_not_fall_back_after_non_transient_gemini_error(monkeypatch):
    class ClientError(Exception):
        code = 400

    calls = []

    async def generate(model, system_prompt, text):
        calls.append(model)
        raise ClientError()

    monkeypatch.setattr(gemini, "MODEL", "primary")
    monkeypatch.setattr(gemini, "FALLBACK_MODEL", "fallback")
    monkeypatch.setattr(gemini, "_generate", generate)

    assert asyncio.run(gemini._call("prompt", "message")) == ""
    assert calls == ["primary"]


def test_plain_array():
    assert _parse_json_array('["no cap", "glow up"]') == ["no cap", "glow up"]


def test_array_of_objects():
    out = _parse_json_array('[{"term": "rizz", "definition": "charisma"}]')
    assert out == [{"term": "rizz", "definition": "charisma"}]


def test_strips_surrounding_prose():
    assert _parse_json_array('Here you go: ["sus"] done') == ["sus"]


def test_strips_code_fence():
    assert _parse_json_array('```json\n["mid"]\n```') == ["mid"]


def test_empty_array():
    assert _parse_json_array("[]") == []


def test_no_array_returns_empty():
    assert _parse_json_array("no json here") == []


def test_invalid_json_returns_empty():
    assert _parse_json_array("[not, valid, json]") == []


def test_non_list_json_returns_empty():
    assert _parse_json_array('{"a": 1}') == []
