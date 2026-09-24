from slangify.sources.gemini import EXTRACT_PROMPT, SYSTEM_PROMPT, _parse_json_array


def test_prompts_exclude_non_slang_terms():
    for prompt in (SYSTEM_PROMPT, EXTRACT_PROMPT):
        assert "ordinary words" in prompt
        assert "When uncertain, exclude it." in prompt


def test_prompts_include_regional_slang():
    for prompt in (SYSTEM_PROMPT, EXTRACT_PROMPT):
        assert "regional and community-specific spoken slang" in prompt
        assert "`nize` is Toronto slang" in prompt


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
