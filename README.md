# slangify

Discord bot that defines the slang in a replied-to message.

## How it works

Two triggers:

**In a server** — reply to a message and `@mention` the bot. Bot replies in the same channel with definitions.
- Default source: **hybrid** (Claude picks slang terms, Urban Dictionary defines them).
- Add `claude` in your mention to use Claude end-to-end: `@slangify claude`.
- Add `urban` to use raw Urban Dictionary tokenization: `@slangify urban`.

**Anywhere (DMs, group DMs, servers)** — install Slangify as a **user app**, then right-click any message → **Apps** → **Define slang** (hybrid), **Define slang (Claude)**, or **Define slang (Urban)**.

## Sources

- **hybrid** (default): Claude reads the message and lists the slang terms it sees (no defs). Each term is then sent to the Urban Dictionary API in parallel; the top definition per term (by `thumbs_up`) is kept. Best signal, crowdsourced phrasing.
- **claude**: Claude returns terms + definitions directly. Smart, can hallucinate.
- **urban**: Tokenize the message, drop stopwords, query Urban Dictionary per token. Noisy — Urban has entries for most English words.

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

**Server install (bot in server):** OAuth2 → URL Generator. Scopes `bot` + `applications.commands`. Permissions: **View Channels**, **Send Messages**, **Read Message History**, **Embed Links**.

**User install (use anywhere):** Discord dev portal → **Installation** tab → enable **User Install**. Copy the **Discord Provided Link** and open it to install Slangify to your account. Context menu commands then appear in any message right-click menu under **Apps**.

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
