# slangify

Discord bot that defines the slang in a replied-to message.

## How it works

Reply to any message in your server and `@mention` the bot. It fetches the replied-to message, identifies slang, and replies in the same channel with definitions.

- Default source: **Claude** (`claude-haiku-4-5`).
- Add `urban` in your mention to use **Urban Dictionary** instead: `@slangify urban`.
- Add `claude` to force Claude explicitly.

## Setup

1. Python 3.11+.
2. Create a Discord application + bot at <https://discord.com/developers/applications>. Enable the **Message Content** privileged intent.
3. Get an Anthropic API key at <https://console.anthropic.com/>.
4. Copy env file and fill in values:
   ```
   cp .env.example .env
   ```
5. Install:
   ```
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```
6. Run:
   ```
   slangify
   ```
   or
   ```
   python -m slangify.bot
   ```

## Invite scopes / permissions

When generating the bot invite URL, include scopes `bot` + `applications.commands` and permissions: **Send Messages**, **Read Message History**, **Embed Links**.

## Layout

```
src/slangify/
├── bot.py         entry point + on_message handler
├── trigger.py     parse @mention text, pick source
├── format.py      Discord embed builder
└── sources/
    ├── urban.py   Urban Dictionary API lookup
    └── claude.py  Claude LLM lookup
```
