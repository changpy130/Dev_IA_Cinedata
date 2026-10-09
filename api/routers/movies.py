from fastapi import APIRouter, Depends, HTTPException
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from api.dependencies import get_sqlite_movie_service
from api.response_models import MovieResponse
from services.movie_service import MovieService, MovieNotFound

router = APIRouter(prefix="/movies")

@router.get("/health", tags=['Monitoring'], description='Check SQLite service availability')
def check_health():
    service: MovieService = get_sqlite_movie_service()

    if service:
        return {
            'message': 'OK'
        }
    else:
        return {
            'message': 'No service found.'
        }

# For future expansion such as adding multiple database connection, change MovieService = Depends(x)
@router.get("/{movielens_id}", tags=['Movies'], response_model=MovieResponse, description='Get movie details with a MovieLens ID')
def get_movie(movielens_id: int, service: MovieService = Depends(get_sqlite_movie_service)):
    try:
        return service.get_movie(movielens_id)

    except MovieNotFound:
        raise HTTPException(status_code=404, detail="Movie not found")