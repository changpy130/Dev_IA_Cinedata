from fastapi import APIRouter, Depends, status
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from api.dependencies import get_sqlite_movie_service
from services.movie_service import MovieService
from api.schema import RatingRequest

router = APIRouter(prefix="/movie/{movielens_id}", tags=['Ratings'])

# 204 status: success, no content
@router.put(
    "/rating", 
    status_code=status.HTTP_204_NO_CONTENT, 
    description='Rate a movie with a MovieLens ID and an user ID.'
)
def upsert_rating(
    movielens_id: int,
    request_body: RatingRequest,
    service: MovieService = Depends(get_sqlite_movie_service)
) -> None:
    service.upsert_rating(user_id=request_body.user_id, movielens_id=movielens_id, rating=request_body.rating)

@router.delete(
    "/rating/{user_id}", 
    status_code=status.HTTP_204_NO_CONTENT, 
    description='Delete a movie rating with a MovieLens ID and an user ID.'
)
def delete_rating(
    movielens_id: int,
    user_id: int,
    service: MovieService = Depends(get_sqlite_movie_service)
) -> None:
    service.delete_rating(user_id=user_id, movielens_id=movielens_id)