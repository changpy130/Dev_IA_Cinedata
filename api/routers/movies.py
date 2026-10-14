from fastapi import APIRouter, Depends, Query, status
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from domain.db_entities import Genre
from api.dependencies import get_sqlite_movie_service
from services.movie_service import MovieService, MovieNotFound, MovieDetailsNotFound
from api.schema import MovieResponse, MovieDetailsResponse, CastMemberResponse, CrewMemberResponse, MovieGenreResponse, RatingRequest, SimilarMovieResponse

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
    return service.get_movie(movielens_id)


@router.get("/{movielens_id}/details", response_model=MovieDetailsResponse, description='Get details of a movie with a MovieLens ID.')
def get_details(
    movielens_id: int, 
    service: MovieService = Depends(get_sqlite_movie_service)
):
    return service.get_details(movielens_id)


@router.get("/{movielens_id}/cast", response_model=list[CastMemberResponse], description='Get cast members of a movie with a MovieLens ID.')
def get_cast(
    movielens_id: int, 
    service: MovieService = Depends(get_sqlite_movie_service)
):
    return service.get_cast(movielens_id)


@router.get("/{movielens_id}/crew", response_model=list[CrewMemberResponse], description='Get crew members of a movie with a MovieLens ID.')
def get_crew(
    movielens_id: int,
    service: MovieService = Depends(get_sqlite_movie_service)
):
    return service.get_crew(movielens_id)


@router.get("/{movielens_id}/genres", response_model=list[MovieGenreResponse], description='Get genre IDs and names of a movie with a MovieLens ID.')
def get_genres(
    movielens_id: int,
    service: MovieService = Depends(get_sqlite_movie_service)
):
    return service.get_genres(movielens_id)

@router.get("/{movielens_id}/similar", response_model=list[SimilarMovieResponse], description='Get a list of similar movies to your targeted movie with a MovieLens ID.')
def get_similar(
    movielens_id: int,
    limit: int = Query(5, ge=1, le=10),
    min_rating: float = Query(4.0, ge=0.5, le=5.0),
    service: MovieService = Depends(get_sqlite_movie_service)
):
    return service.get_similar_movies_with_details(
        movielens_id=movielens_id,
        min_rating=min_rating,
        limit=limit
    )

# 204 status: success, no content
@router.put("/{movielens_id}/rating", status_code=status.HTTP_204_NO_CONTENT, description='Rate a movie with a MovieLens ID and an user ID.')
def upsert_rating(
    movielens_id: int,
    request_body: RatingRequest,
    service: MovieService = Depends(get_sqlite_movie_service)
) -> None:
    service.upsert_rating(user_id=request_body.user_id, movielens_id=movielens_id, rating=request_body.rating)

@router.delete("/{movielens_id}/rating/{user_id}", status_code=status.HTTP_204_NO_CONTENT, description='Delete a movie rating with a MovieLens ID and an user ID.')
def delete_rating(
    movielens_id: int,
    user_id: int,
    service: MovieService = Depends(get_sqlite_movie_service)
) -> None:
    service.delete_rating(user_id=user_id, movielens_id=movielens_id)