from slangify.format import FIELD_VALUE_LIMIT, MAX_FIELDS, build_embed
from slangify.sources import Definition


def _defs(n: int) -> list[Definition]:
    return [Definition(term=f"t{i}", definition=f"d{i}") for i in range(n)]


def test_footer_labels_source():
    embed = build_embed(_defs(1), "hybrid")
    assert "Gemini → Urban Dictionary" in embed.footer.text


def test_unknown_source_label_passthrough():
    embed = build_embed(_defs(1), "weird")
    assert "weird" in embed.footer.text


def test_caps_fields_and_adds_more_marker():
    embed = build_embed(_defs(MAX_FIELDS + 3), "gemini")
    # MAX_FIELDS definition fields + 1 "+N more" field
    assert len(embed.fields) == MAX_FIELDS + 1
    assert embed.fields[-1].value == "+3 more"


def test_no_more_marker_when_within_cap():
    embed = build_embed(_defs(MAX_FIELDS), "gemini")
    assert len(embed.fields) == MAX_FIELDS
    assert all("more" not in (f.value or "") for f in embed.fields)


def test_truncates_long_value():
    long_def = "x" * (FIELD_VALUE_LIMIT + 100)
    embed = build_embed([Definition(term="t", definition=long_def)], "gemini")
    assert len(embed.fields[0].value) <= FIELD_VALUE_LIMIT
    assert embed.fields[0].value.endswith("…")


def test_example_rendered_when_present():
    embed = build_embed([Definition(term="t", definition="d", example="ex")], "urban")
    assert "Example" in embed.fields[0].value
    assert "ex" in embed.fields[0].value
