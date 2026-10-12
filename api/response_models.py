from pydantic import BaseModel
from datetime import date

class MovieResponse(BaseModel):
    movielens_id: int
    title: str
    year: int | None

class MovieDetailsResponse(BaseModel):
    movielens_id: int
    title: str
    year: int | None
    release_date: date | None
    budget: int | None
    revenue: int | None
    runtime: int | None
    vote_average: float | None
    tagline: str | None
    plot: str | None

class CastMemberResponse(BaseModel):
    person_id: int
    name: str
    character: str | None

class MovieGenreResponse(BaseModel):
    genre_id: int
    genre_name: str