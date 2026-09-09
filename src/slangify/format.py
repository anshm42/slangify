import discord

from .sources import Definition

FIELD_VALUE_LIMIT = 1024
MAX_FIELDS = 5

SOURCE_LABELS = {
    "urban": "Urban Dictionary",
    "gemini": "Gemini",
    "hybrid": "Gemini → Urban Dictionary",
}


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def build_embed(definitions: list[Definition], source: str) -> discord.Embed:
    embed = discord.Embed(title="Slang in replied message", color=0x5865F2)
    embed.set_footer(text=f"Source: {SOURCE_LABELS.get(source, source)}")

    shown = definitions[:MAX_FIELDS]
    for d in shown:
        value = d.definition
        if d.example:
            value = f"{value}\n\n*Example:* {d.example}"
        embed.add_field(
            name=_truncate(d.term, 256),
            value=_truncate(value, FIELD_VALUE_LIMIT),
            inline=False,
        )

    extra = len(definitions) - len(shown)
    if extra > 0:
        embed.add_field(name="…", value=f"+{extra} more", inline=False)

    return embed
