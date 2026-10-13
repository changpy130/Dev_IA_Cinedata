from dataclasses import dataclass
from enum import Enum
from datetime import date

@dataclass(frozen=True)
class Movie:
    movielens_id: int
    title: str
    year: int | None

@dataclass(frozen=True)
class MovieDetails:
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

@dataclass(frozen=True)
class CastMember:
    person_id: int
    name: str
    character: str | None

@dataclass(frozen=True)
class CrewMember:
    person_id: int
    name: str
    job: str | None

@dataclass(frozen=True)
class MovieGenre:
    genre_id: int
    genre_name: str

@dataclass(frozen=True)
class Rating:
    user_id: int
    movielens_id: int
    rating: float

class Genre(str, Enum):
    ACTION = "Action"
    ADVENTURE = "Adventure"
    ANIMATION = "Animation"
    COMEDY = "Comedy"
    CRIME = "Crime"
    DOCUMENTARY = "Documentary"
    DRAMA = "Drama"
    FAMILY = "Family"
    FANTASY = "Fantasy"
    HISTORY = "History"
    HORROR = "Horror"
    MUSIC = "Music"
    MYSTERY = "Mystery"
    ROMANCE = "Romance"
    SCIENCE_FICTION = "Science Fiction"
    THRILLER = "Thriller"
    TV_MOVIE = "TV Movie"
    WAR = "War"
    WESTERN = "Western"