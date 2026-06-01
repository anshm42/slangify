import re
from dataclasses import dataclass
from typing import Literal

Source = Literal["urban", "claude", "hybrid"]

DEFAULT_SOURCE: Source = "hybrid"


@dataclass
class TriggerInput:
    source: Source


def parse(content: str, bot_user_id: int) -> TriggerInput:
    text = re.sub(rf"<@!?{bot_user_id}>", " ", content).lower()
    tokens = set(text.split())
    if "urban" in tokens:
        return TriggerInput(source="urban")
    if "claude" in tokens:
        return TriggerInput(source="claude")
    if "hybrid" in tokens:
        return TriggerInput(source="hybrid")
    return TriggerInput(source=DEFAULT_SOURCE)
