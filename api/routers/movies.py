from fastapi import APIRouter, Depends, Query
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from domain.db_entities import Genre
from api.dependencies import get_sqlite_movie_service, get_content_similarity_service
from services.movie_service import MovieService
from services.content_similarity_service import ContentSimilarityService
from api.schema import MovieResponse, MovieDetailsResponse, MovieGenreResponse, SimilarMovieResponse

router = APIRouter(prefix="/movie", tags=['Movies'])

@router.get(
    "/list",
    response_model=list[MovieResponse], 
    description='Get a list of movies.'
)
def list_movies(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    year: int | None = Query(None, ge=1888, le=2100),
    genre: Genre | None = None,
    service: MovieService = Depends(get_sqlite_movie_service)
):
    return service.list_movies(limit=limit, offset=offset, year=year, genre=genre.value if genre else None)

@router.get(
    "/search", 
    response_model=list[MovieResponse], 
    description='Search movies by a keyword in the title'
)
def search_movies(
    keyword: str = Query(..., min_length=2, max_length=100),  # ""..."" means "required"
    limit: int = Query(5, ge=1, le=20),
    service: MovieService = Depends(get_sqlite_movie_service)
):
    return service.search_movies(query=keyword, limit=limit)

# For future expansion such as adding multiple database connection, change MovieService = Depends(x)
@router.get(
    "/{movielens_id}", 
    response_model=MovieResponse, 
    description='Get a movie with a MovieLens ID, including: MovieLens ID, title and year.'
)
def get_movie(
    movielens_id: int, 
    service: MovieService = Depends(get_sqlite_movie_service)
):
    return service.get_movie(movielens_id)


@router.get(
    "/{movielens_id}/details", 
    response_model=MovieDetailsResponse, 
    description='Get details of a movie with a MovieLens ID.'
)
def get_details(
    movielens_id: int, 
    service: MovieService = Depends(get_sqlite_movie_service)
):
    return service.get_details(movielens_id)


@router.get(
    "/{movielens_id}/genres", 
    response_model=list[MovieGenreResponse], 
    description='Get genre IDs and names of a movie with a MovieLens ID.'
)
def get_genres(
    movielens_id: int,
    service: MovieService = Depends(get_sqlite_movie_service)
):
    return service.get_genres(movielens_id)


#region Recommendation

@router.get(
    "/{movielens_id}/similar", 
    response_model=list[SimilarMovieResponse], 
    description='Get a list of similar movies to your targeted movie with a MovieLens ID, by Jaccard Similarity mesure.'
)
def get_similar(
    movielens_id: int,
    limit: int = Query(5, ge=1, le=20),
    min_rating: float = Query(4.0, ge=0.5, le=5.0),
    service: MovieService = Depends(get_sqlite_movie_service)
):
    return service.get_similar_movies_with_details(
        movielens_id=movielens_id,
        min_rating=min_rating,
        limit=limit
    )

@router.get(
    "/{movielens_id}/similar-content",
    response_model=list[SimilarMovieResponse],
    description='Get a list of text-based similar movies to your targeted movie.'
)
def get_similar_by_content(
    movielens_id: int,
    limit: int = Query(5, ge=1, le=20),
    service: ContentSimilarityService = Depends(get_content_similarity_service)
):
    return service.get_similar_by_content_with_details(movielens_id=movielens_id, limit=limit)