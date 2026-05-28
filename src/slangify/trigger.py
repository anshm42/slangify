import re
from dataclasses import dataclass
from typing import Literal

Source = Literal["urban", "claude"]


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
    return TriggerInput(source="claude")
