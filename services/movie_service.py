import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from domain.db_entities import Movie
from domain.repositories import MovieRepository

class MovieNotFound(Exception):
    pass

class MovieService:
    def __init__(self, repo: MovieRepository):
        self._repo = repo

    def get_movie(self, movielens_id: int) -> Movie:
        movie = self._repo.get_by_id(movielens_id)
        if movie is None:
            raise MovieNotFound(movielens_id)
        return movie