# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Slangify is a Discord bot that explains slang in a referenced message. Implemented as an installable package under `src/slangify/`; console entry point `slangify.bot:main`.

## Stack

- Python 3.11+
- `discord.py` 2.x — bot framework
- `anthropic` — Claude SDK (slang definitions via LLM)
- `aiohttp` — Urban Dictionary API calls
- `python-dotenv` — load secrets

## Build & run

- Install editable (with dev deps): `pip install -e ".[dev]"` (in a venv).
- Run: `slangify` (console script) or `python -m slangify.bot`.
- Tests: `pytest` (pure-function unit tests in `tests/`, no network). No lint config yet.

## Trigger semantics

Two triggers, both supported:

**A. Server: reply + @mention** (`on_message`)
1. Ignore bots; require `bot.user in message.mentions` and `message.reference is not None`.
2. Fetch replied-to message via `message.channel.fetch_message(message.reference.message_id)`.
3. Parse mention text for source flag (`urban` / `claude` / `hybrid`, default `hybrid`) via `trigger.parse`.
4. Reply with embed via `message.reply(...)`.

**B. User-app message context menu** (`app_commands.context_menu`)
- Three context menu commands registered: `Define slang` (hybrid), `Define slang (Claude)`, `Define slang (Urban)`.
- All decorated with `@app_commands.allowed_installs(guilds=True, users=True)` and `@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)` so they work in DMs/GDMs as a user-installed app.
- Must `interaction.response.defer(thinking=True)` before lookup (3s response window) then `interaction.followup.send(embed=...)`.
- Commands synced on `on_ready` via `tree.sync()`.

## Sources

- `sources/hybrid.py` — default. Uses `claude.extract_terms(text)` then `urban.fetch_terms(terms)` to combine semantic filtering with crowdsourced definitions.
- `sources/claude.py` — `lookup(text)` returns terms + defs from Claude; `extract_terms(text)` returns just the term list. Both share `_call()` and the cached system prompt.
- `sources/urban.py` — `lookup(text)` tokenizes + queries (legacy path); `fetch_terms(terms)` queries pre-supplied terms in parallel; `fetch_term(session, term)` is the single-term primitive.

## Required env vars

Loaded from `.env` at startup (fail fast if missing):

- `DISCORD_TOKEN`
- `ANTHROPIC_API_KEY`

## Discord intents

`message_content` is required (privileged — must be enabled in the Discord developer portal). Also enable `guilds` and `messages`.

## Layout

```
src/slangify/
├── bot.py         (entry, on_message handler, context menu registration)
├── trigger.py     (parse @mention + reply, extract source flag)
├── sources/
│   ├── __init__.py (shared Definition dataclass)
│   ├── urban.py   (Urban Dictionary lookup)
│   ├── claude.py  (Claude slang explanation, claude-haiku-4-5)
│   └── hybrid.py  (Claude extracts terms → Urban defines)
└── format.py      (Discord embed builder)
```

The shared `Definition` dataclass (term / definition / example) lives in `sources/__init__.py` — all sources return `list[Definition]`.

## Conventions

- Default Claude model for definitions: `claude-haiku-4-5` (fast, cheap, short outputs).
- Enable prompt caching on the Claude system prompt (`cache_control: {type: "ephemeral"}`) — it's reused across calls.
- Urban Dictionary: cap at 5 tokens per call, parallel via `asyncio.gather`, keep top definition by `thumbs_up`.
- Discord embed field limit: 1024 chars per value, cap at 5 fields, append "+N more" if truncated.
