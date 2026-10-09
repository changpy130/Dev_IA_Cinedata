from dataclasses import dataclass

@dataclass(frozen=True)
class Movie:
    movielens_id: int
    title: str
    year: int | None