"""
    Transform text for search_movies() and avoid including meaningless words.
"""

import re

_LEADING_ARTICLE = re.compile(
    r"^(the|a|an|le|la|les|el|los|las|il|un|una|une|der|die|das|det)\s+|^l'",
    re.IGNORECASE,
)


def normalise_query(query: str) -> str:
    query = query.strip()
    stripped = _LEADING_ARTICLE.sub("", query, count=1)
    return stripped or query