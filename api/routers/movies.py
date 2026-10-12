from fastapi import APIRouter, Depends, HTTPException, Query
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from domain.db_entities import Genre
from api.dependencies import get_sqlite_movie_service
from services.movie_service import MovieService, MovieNotFound, MovieDetailsNotFound
from api.response_models import MovieResponse, MovieDetailsResponse, CastMemberResponse, MovieGenreResponse

router = APIRouter(prefix="/movies", tags=['Movies'])

@router.get("", response_model=list[MovieResponse], description='Get a list of movies.')
def list_movies(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    year: int | None = Query(None, ge=1888, le=2100),
    genre: Genre | None = None,
    service: MovieService = Depends(get_sqlite_movie_service)
):
    return service.list_movies(limit=limit, offset=offset, year=year, genre=genre.value if genre else None)


# For future expansion such as adding multiple database connection, change MovieService = Depends(x)
@router.get("/{movielens_id}", response_model=MovieResponse, description='Get a movie with a MovieLens ID, including: MovieLens ID, title and year.')
def get_movie(
    movielens_id: int, 
    service: MovieService = Depends(get_sqlite_movie_service)
):
    try:
        return service.get_movie(movielens_id)

    except MovieNotFound:
        raise HTTPException(status_code=404, detail="Movie not found.")


@router.get("/{movielens_id}/details", response_model=MovieDetailsResponse, description='Get details of a movie with a MovieLens ID.')
def get_details(
    movielens_id: int, 
    service: MovieService = Depends(get_sqlite_movie_service)
):
    try:
        return service.get_details(movielens_id)
    
    except MovieDetailsNotFound:
        raise HTTPException(status_code=404, detail="No details available.")


@router.get("/{movielens_id}/cast", response_model=list[CastMemberResponse], description='Get cast members of a movie with a MovieLens ID.')
def get_cast(
    movielens_id: int, 
    service: MovieService = Depends(get_sqlite_movie_service)
):
    try:
        return service.get_cast(movielens_id)

    except MovieNotFound:
        raise HTTPException(status_code=404, detail="No cast infos available.")


@router.get("/{movielens_id}/genres", response_model=list[MovieGenreResponse], description='Get genre IDs and names of a movie with a MovieLens ID.')
def get_genres(
    movielens_id: int,
    service: MovieService = Depends(get_sqlite_movie_service)
):
    try:
        return service.get_genres(movielens_id)

    except MovieNotFound:
        raise HTTPException(status_code=404, detail="No genre infos available.")