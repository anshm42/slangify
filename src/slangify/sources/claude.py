import json
import logging
import os
import re

from anthropic import AsyncAnthropic

from . import Definition

log = logging.getLogger(__name__)

MODEL = "claude-haiku-4-5"
MAX_TOKENS = 512

SYSTEM_PROMPT = (
    "You identify slang, internet jargon, and non-literal expressions in a user-provided "
    "message and define each term concisely (one or two sentences per term). "
    "Output ONLY a JSON array of objects with keys `term` and `definition`. "
    "If no slang or jargon is present, output an empty JSON array: []. "
    "Do not include commentary, code fences, or prose outside the JSON."
)

EXTRACT_PROMPT = (
    "You identify slang, internet jargon, and non-literal expressions in a user-provided "
    "message and return ONLY the terms (no definitions). "
    "Output ONLY a JSON array of strings, lowercased, deduplicated, max 5 items. "
    "Multi-word phrases are allowed and sentences are allowed (e.g. \"no cap\", \"glow up\"). "
    "define within the context of the sentence it is used."
    "If no slang or jargon is present, output an empty JSON array: []. "
    "Do not include commentary, code fences, or prose outside the JSON."
)

_client: AsyncAnthropic | None = None


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
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
    if not isinstance(parsed, list):
        return []
    return parsed


async def _call(system_prompt: str, text: str) -> str:
    client = _get_client()
    try:
        resp = await client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": text}],
        )
    except Exception:
        log.exception("Claude API call failed")
        return ""
    return "".join(block.text for block in resp.content if getattr(block, "type", None) == "text")


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
