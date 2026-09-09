from slangify.trigger import parse

BOT_ID = 123


def _mention(rest: str) -> str:
    return f"<@{BOT_ID}> {rest}".strip()


def test_default_is_hybrid():
    assert parse(_mention(""), BOT_ID).source == "hybrid"


def test_urban_flag():
    assert parse(_mention("urban"), BOT_ID).source == "urban"


def test_gemini_flag():
    assert parse(_mention("gemini"), BOT_ID).source == "gemini"


def test_explicit_hybrid_flag():
    assert parse(_mention("hybrid"), BOT_ID).source == "hybrid"


def test_flag_is_case_insensitive():
    assert parse(_mention("URBAN"), BOT_ID).source == "urban"


def test_urban_wins_over_gemini_when_both_present():
    # parse checks urban first
    assert parse(_mention("urban gemini"), BOT_ID).source == "urban"


def test_nickname_mention_form():
    assert parse(f"<@!{BOT_ID}> urban", BOT_ID).source == "urban"


def test_unknown_word_falls_back_to_default():
    assert parse(_mention("please define"), BOT_ID).source == "hybrid"
