import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from domain.db_entities import Movie, MovieDetails, Rating, CoLikeCount


class FakeMovieRepository:
    def __init__(
        self, 
        movies: list[Movie] | None = None, 
        details: list[MovieDetails] | None = None
    ) -> None:
        self._movies = { m.movielens_id: m for m in movies or [] }
        self._ratings: dict[tuple[int, int], float] = {}
        self._details = {d.movielens_id: d for d in details or []}

        
    def get_by_id(self, movielens_id: int) -> Movie | None:
        return self._movies.get(movielens_id)

    def get_details(self, movielens_id: int) -> MovieDetails | None:
        return self._details.get(movielens_id)

    def upsert_rating(self, rating: Rating) -> None:
        self._ratings[(rating.user_id, rating.movielens_id)] = rating.rating

    def delete_rating(self, user_id: int, movielens_id: int) -> bool:
        if (user_id, movielens_id) in self._ratings:
            del self._ratings[(user_id, movielens_id)]
            return True
        return False

    def count_likes(self, movielens_id: int, min_rating: float = 4.0) -> int:
        return 10

    def get_co_like_counts(self, movielens_id: int, min_rating: float = 4.0) -> list[CoLikeCount]:
        return [
            CoLikeCount(movielens_id=10, co_likes=5, likes=20),
            CoLikeCount(movielens_id=20, co_likes=2, likes=1000),  # lowest score
            CoLikeCount(movielens_id=30, co_likes=8, likes=10),  # highest score
        ]

    def search_by_title(self, query: str, limit: int) -> list[Movie]:
        q = query.lower()
        matches = [m for m in self._movies.values() if q in m.title.lower()]
        return matches[:limit]