import asyncio
import re
import string

import aiohttp

from . import Definition

URBAN_API = "https://api.urbandictionary.com/v0/define"

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "and", "or", "but", "if", "then", "else", "of", "to", "in", "on", "at",
    "by", "for", "with", "as", "from", "this", "that", "these", "those",
    "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us",
    "them", "my", "your", "his", "its", "our", "their", "do", "does", "did",
    "have", "has", "had", "will", "would", "can", "could", "should", "may",
    "might", "must", "not", "no", "yes", "so", "too", "very", "just", "now",
    "here", "there", "what", "which", "who", "when", "where", "why", "how",
    "all", "any", "some", "more", "most", "less", "than", "also", "only",
}

MAX_TERMS = 5


def _tokenize(text: str) -> list[str]:
    cleaned = re.sub(r"<@!?\d+>", " ", text)
    cleaned = re.sub(r"https?://\S+", " ", cleaned)
    raw = cleaned.lower().split()
    seen: set[str] = set()
    tokens: list[str] = []
    for tok in raw:
        tok = tok.strip(string.punctuation)
        if not tok or tok in STOPWORDS or tok in seen:
            continue
        if not any(c.isalpha() for c in tok):
            continue
        seen.add(tok)
        tokens.append(tok)
    return tokens[:MAX_TERMS]


async def _fetch_term(session: aiohttp.ClientSession, term: str) -> Definition | None:
    try:
        async with session.get(URBAN_API, params={"term": term}, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return None

    entries = data.get("list") or []
    if not entries:
        return None
    top = max(entries, key=lambda e: e.get("thumbs_up", 0))
    definition = (top.get("definition") or "").replace("[", "").replace("]", "").strip()
    example = (top.get("example") or "").replace("[", "").replace("]", "").strip() or None
    if not definition:
        return None
    return Definition(term=term, definition=definition, example=example)


async def lookup(text: str) -> list[Definition]:
    terms = _tokenize(text)
    if not terms:
        return []
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*(_fetch_term(session, t) for t in terms))
    return [r for r in results if r is not None]
