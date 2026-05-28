# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Slangify is a Discord bot that explains slang in a referenced message. The repo is currently empty (no code yet) — implementation follows the design in `/Users/am/.claude/plans/i-want-to-make-cryptic-noodle.md`.

## Stack (planned)

- Python 3.11+
- `discord.py` 2.x — bot framework
- `anthropic` — Claude SDK (slang definitions via LLM)
- `aiohttp` — Urban Dictionary API calls
- `python-dotenv` — load secrets

## Trigger semantics

The bot is triggered by **reply + @mention**, not slash commands. Flow:

1. User replies to some message AND @mentions the bot in their reply.
2. `on_message` handler: ignore bots, require `bot.user in message.mentions` and `message.reference is not None`.
3. Fetch the replied-to message via `message.channel.fetch_message(message.reference.message_id)`.
4. Parse the mention text for a source flag: `urban` → Urban Dictionary, `claude` → Claude, default → Claude.
5. Reply with an embed in the same channel via `message.reply(...)`.

## Required env vars

Loaded from `.env` at startup (fail fast if missing):

- `DISCORD_TOKEN`
- `ANTHROPIC_API_KEY`

## Discord intents

`message_content` is required (privileged — must be enabled in the Discord developer portal). Also enable `guilds` and `messages`.

## Planned layout

```
src/slangify/
├── bot.py         (entry, on_message handler)
├── trigger.py     (parse @mention + reply, extract source flag)
├── sources/
│   ├── urban.py   (Urban Dictionary lookup)
│   └── claude.py  (Claude slang explanation, claude-haiku-4-5)
└── format.py      (Discord embed builder)
```

## Conventions

- Default Claude model for definitions: `claude-haiku-4-5` (fast, cheap, short outputs).
- Enable prompt caching on the Claude system prompt (`cache_control: {type: "ephemeral"}`) — it's reused across calls.
- Urban Dictionary: cap at 5 tokens per call, parallel via `asyncio.gather`, keep top definition by `thumbs_up`.
- Discord embed field limit: 1024 chars per value, cap at 5 fields, append "+N more" if truncated.
