from . import Definition
from . import claude as claude_source
from . import urban as urban_source


async def lookup(text: str) -> list[Definition]:
    terms = await claude_source.extract_terms(text)
    if not terms:
        return []
    return await urban_source.fetch_terms(terms)
