import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from domain.db_entities import Movie, MovieDetails, CastMember, MovieGenre
from domain.repositories import MovieRepository

class MovieNotFound(Exception):
    pass

class MovieDetailsNotFound(Exception):
    pass

class MovieService:
    def __init__(self, repo: MovieRepository):
        self._repo = repo

    def get_movie(self, movielens_id: int) -> Movie:
        movie = self._repo.get_by_id(movielens_id)

        if movie is None:
            raise MovieNotFound(movielens_id)
        return movie


    def list_movies(self, limit: int, offset: int, year: int | None = None, genre: str | None = None) -> list[Movie]:
        return self._repo.list_movies(limit=limit, offset=offset, year=year, genre=genre)


    def get_details(self, movielens_id: int) -> MovieDetails | None: 
        details = self._repo.get_details(movielens_id=movielens_id)

        if details is None:
            raise MovieDetailsNotFound(movielens_id)
        return details

    def get_cast(self, movielens_id: int) -> list[CastMember]:
        self.get_movie(movielens_id)  # check if the movie exists; if not, it will reuse the MovieNotFound exception.
        return self._repo.get_cast(movielens_id=movielens_id)

    def get_genres(self, movielens_id: int) -> list[MovieGenre]:
        self.get_movie(movielens_id)
        return self._repo.get_genres(movielens_id=movielens_id)