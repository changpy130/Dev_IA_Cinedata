import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from domain.db_entities import Movie, Rating


class FakeMovieRepository:
    def __init__(self, movies: list[Movie] | None = None) -> None:
        self._movies = { m.movielens_id: m for m in movies or [] }
        self._ratings: dict[tuple[int, int], float] = {}

        
    def get_by_id(self, movielens_id: int) -> Movie | None:
        return self._movies.get(movielens_id)

    def upsert_rating(self, rating: Rating) -> None:
        self._ratings[(rating.user_id, rating.movielens_id)] = rating.rating

    def delete_rating(self, user_id: int, movielens_id: int) -> bool:
        if (user_id, movielens_id) in self._ratings:
            del self._ratings[(user_id, movielens_id)]
            return True
        return False