from pydantic import BaseModel, Field
from datetime import date

#region Response
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

class CrewMemberResponse(BaseModel):
    person_id: int
    name: str
    job: str | None

class MovieGenreResponse(BaseModel):
    genre_id: int
    genre_name: str

class SimilarMovieResponse(BaseModel):
    details: MovieDetailsResponse
    score: float


#region Request
class RatingRequest(BaseModel):
    user_id: int
    rating: float = Field(ge=0.5, le=5, multiple_of=0.5)