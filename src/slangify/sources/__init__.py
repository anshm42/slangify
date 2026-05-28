from dataclasses import dataclass


@dataclass
class Definition:
    term: str
    definition: str
    example: str | None = None
