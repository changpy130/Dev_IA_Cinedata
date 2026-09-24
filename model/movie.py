from pydantic import BaseModel
from typing import Optional

class Movie(BaseModel):
    id: int
    title: str
    release_date: str
    poster_path: str
    overview: str
    genre_ids: list

class PopularMoviesResponse(BaseModel):
    page: int
    results: list[Movie]
    total_pages: int


#region Movie Details
class Genre(BaseModel):
    id: int
    name: str

class MoviewDetails(BaseModel):
    id: int
    imdb_id: str
    title: str
    release_date: str
    genres: list[Genre]
    origin_country: list
    original_title: str
    budget: int
    revenue: int
    runtime: int
    vote_average: float
    tagline: str

#region Credit
class Cast(BaseModel):
    id: int
    name: str
    character: str
    profile_path: Optional[str] = None
    known_for_department: str

class Crew(BaseModel):
    id: int
    name: str
    job: str
    profile_path: Optional[str] = None
    known_for_department: str

class Credit(BaseModel):
    id: int
    cast: list[Cast]
    crew: list[Crew]