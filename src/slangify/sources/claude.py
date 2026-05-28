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

_client: AsyncAnthropic | None = None


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def _extract_json_array(text: str) -> list[dict]:
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
    return [item for item in parsed if isinstance(item, dict)]


async def lookup(text: str) -> list[Definition]:
    client = _get_client()
    try:
        resp = await client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": text}],
        )
    except Exception:
        log.exception("Claude API call failed")
        return []

    body = "".join(block.text for block in resp.content if getattr(block, "type", None) == "text")
    items = _extract_json_array(body)
    out: list[Definition] = []
    for item in items:
        term = (item.get("term") or "").strip()
        definition = (item.get("definition") or "").strip()
        if term and definition:
            out.append(Definition(term=term, definition=definition))
    return out
