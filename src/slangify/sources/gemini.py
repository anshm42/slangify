import json
import logging
import os
import re

from google import genai
from google.genai import types

from . import Definition

log = logging.getLogger(__name__)

MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

SYSTEM_PROMPT = (
    "You identify only slang (including regional and community-specific spoken slang), established "
    "internet jargon, and idiomatic or non-literal "
    "expressions in a user-provided message. A term qualifies only when its intended meaning "
    "differs from its ordinary dictionary meaning or requires online/community context to "
    "understand. Do not include ordinary words, standard phrases, proper nouns, technical terms, "
    "or simple abbreviations whose meaning is clear from the message. For example, `nize` is "
    "Toronto slang and should be included when used with its slang meaning. When uncertain, exclude it. "
    "Define each qualifying term concisely (one or two sentences per term). "
    "Output a JSON array of objects with keys `term` and `definition`. "
    "If no slang or jargon is present, output an empty JSON array: []."
)

EXTRACT_PROMPT = (
    "You identify only slang (including regional and community-specific spoken slang), established "
    "internet jargon, and idiomatic or non-literal "
    "expressions in a user-provided message. A term qualifies only when its intended meaning "
    "differs from its ordinary dictionary meaning or requires online/community context to "
    "understand. Do not include ordinary words, standard phrases, proper nouns, technical terms, "
    "or simple abbreviations whose meaning is clear from the message. For example, `nize` is "
    "Toronto slang and should be included when used with its slang meaning. When uncertain, exclude it. "
    "Return a JSON array of only the qualifying terms, lowercased, deduplicated, max 5 items. "
    "Multi-word phrases are allowed (for example, \"no cap\" or \"glow up\"). "
    "If no slang or jargon is present, output an empty JSON array: []."
)

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _client


def _parse_json_array(text: str) -> list:
    text = text.strip()
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        return []
    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []


async def _call(system_prompt: str, text: str) -> str:
    try:
        response = await _get_client().aio.models.generate_content(
            model=MODEL,
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                max_output_tokens=512,
            ),
        )
    except Exception:
        log.exception("Gemini API call failed")
        return ""
    try:
        return response.text or ""
    except Exception:
        log.exception("Gemini API returned no text")
        return ""


async def lookup(text: str) -> list[Definition]:
    body = await _call(SYSTEM_PROMPT, text)
    items = [item for item in _parse_json_array(body) if isinstance(item, dict)]
    out: list[Definition] = []
    for item in items:
        term = (item.get("term") or "").strip()
        definition = (item.get("definition") or "").strip()
        if term and definition:
            out.append(Definition(term=term, definition=definition))
    return out


async def extract_terms(text: str) -> list[str]:
    body = await _call(EXTRACT_PROMPT, text)
    items = _parse_json_array(body)
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if not isinstance(item, str):
            continue
        term = item.strip().lower()
        if term and term not in seen:
            seen.add(term)
            out.append(term)
        if len(out) >= 5:
            break
    return out
