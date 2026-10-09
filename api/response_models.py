from pydantic import BaseModel

class MovieResponse(BaseModel):
    movielens_id: int
    title: str
    year: int | None