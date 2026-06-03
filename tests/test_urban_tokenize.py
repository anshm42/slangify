from slangify.sources.urban import MAX_TERMS, _tokenize


def test_drops_stopwords():
    assert _tokenize("the and of to") == []


def test_keeps_slangish_tokens():
    assert _tokenize("bussin meal fr") == ["bussin", "meal", "fr"]


def test_strips_punctuation():
    assert _tokenize("sus!") == ["sus"]


def test_dedupes_preserving_order():
    assert _tokenize("rizz rizz cap rizz") == ["rizz", "cap"]


def test_caps_at_max_terms():
    text = "alpha bravo charlie delta echo foxtrot golf"
    assert len(_tokenize(text)) == MAX_TERMS


def test_strips_mentions_and_urls():
    assert _tokenize("<@123> check https://example.com sus") == ["check", "sus"]


def test_drops_pure_numbers():
    assert _tokenize("100 sus") == ["sus"]


def test_lowercases():
    assert _tokenize("SUS Cap") == ["sus", "cap"]
