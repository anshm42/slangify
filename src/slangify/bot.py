import logging
import os
import sys

import discord
from dotenv import load_dotenv

from .format import build_embed
from .sources import Definition
from .sources import claude as claude_source
from .sources import urban as urban_source
from .trigger import parse

log = logging.getLogger("slangify")

REQUIRED_ENV = ("DISCORD_TOKEN", "ANTHROPIC_API_KEY")


def _load_env() -> str:
    load_dotenv()
    missing = [name for name in REQUIRED_ENV if not os.environ.get(name)]
    if missing:
        sys.exit(f"Missing required env vars: {', '.join(missing)}. Copy .env.example to .env and fill in values.")
    return os.environ["DISCORD_TOKEN"]


async def _lookup(source: str, text: str) -> list[Definition]:
    if source == "urban":
        return await urban_source.lookup(text)
    return await claude_source.lookup(text)


def _build_client() -> discord.Client:
    intents = discord.Intents.default()
    intents.message_content = True
    intents.messages = True
    intents.guilds = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready() -> None:
        log.info("Logged in as %s (id=%s)", client.user, getattr(client.user, "id", "?"))

    @client.event
    async def on_message(message: discord.Message) -> None:
        if message.author.bot:
            return
        if client.user is None or client.user not in message.mentions:
            return

        if message.reference is None or message.reference.message_id is None:
            await message.reply("Reply to a message and @mention me to define the slang in it.", mention_author=False)
            return

        try:
            target = await message.channel.fetch_message(message.reference.message_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            await message.reply("Couldn't fetch the replied-to message.", mention_author=False)
            return

        text = (target.content or "").strip()
        if not text:
            await message.reply("Replied-to message has no text to define.", mention_author=False)
            return

        trigger = parse(message.content, client.user.id)
        try:
            definitions = await _lookup(trigger.source, text)
        except Exception:
            log.exception("Lookup failed (source=%s)", trigger.source)
            await message.reply("Something went wrong looking up that slang.", mention_author=False)
            return

        if not definitions:
            await message.reply("No slang found in that message.", mention_author=False)
            return

        embed = build_embed(definitions, trigger.source)
        await message.reply(embed=embed, mention_author=False)

    return client


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    token = _load_env()
    client = _build_client()
    client.run(token, log_handler=None)


if __name__ == "__main__":
    main()
