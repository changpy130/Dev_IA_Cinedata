from fastapi import APIRouter, Depends
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from api.dependencies import get_sqlite_movie_service
from services.movie_service import MovieService
from api.schema import CastMemberResponse, CrewMemberResponse

router = APIRouter(prefix="/movie/{movielens_id}", tags=['Credits'])

@router.get(
    "/cast", 
    response_model=list[CastMemberResponse], 
    description='Get cast members of a movie with a MovieLens ID.'
)
def get_cast(
    movielens_id: int, 
    service: MovieService = Depends(get_sqlite_movie_service)
):
    return service.get_cast(movielens_id)


@router.get(
    "/crew", 
    response_model=list[CrewMemberResponse], 
    description='Get crew members of a movie with a MovieLens ID.'
)
def get_crew(
    movielens_id: int,
    service: MovieService = Depends(get_sqlite_movie_service)
):
    return service.get_crew(movielens_id)