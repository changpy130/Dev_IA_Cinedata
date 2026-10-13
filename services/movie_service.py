import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from domain.db_entities import Movie, MovieDetails, CastMember, CrewMember, MovieGenre, Rating
from domain.repositories import MovieRepository

#region Error class
class NotFoundError(Exception):
    pass

class MovieNotFound(NotFoundError):
    def __init__(self, movielens_id: int):
        super().__init__(f"Movie {movielens_id} not found")

class MovieDetailsNotFound(NotFoundError):
    def __init__(self, movielens_id: int):
        super().__init__(f"Movie {movielens_id} details not found")

class RatingNotFound(NotFoundError):
    def __init__(self, user_id: int, movielens_id: int):
        super().__init__(f"Rating by user {user_id} for the movie {movielens_id} not found")


#region Main service
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


    def get_crew(self, movielens_id: int) -> list[CrewMember]:
        self.get_movie(movielens_id)
        return self._repo.get_crew(movielens_id=movielens_id)


    def get_genres(self, movielens_id: int) -> list[MovieGenre]:
        self.get_movie(movielens_id)
        return self._repo.get_genres(movielens_id=movielens_id)

    def upsert_rating(self, user_id: int, movielens_id: int, rating: float) -> None:
        self.get_movie(movielens_id)
        rating_entity = Rating(user_id, movielens_id, rating)
        self._repo.upsert_rating(rating=rating_entity)

    def delete_rating(self, user_id: int, movielens_id: int) -> None:
        self.get_movie(movielens_id)
        is_deleted = self._repo.delete_rating(user_id=user_id, movielens_id=movielens_id)
        
        if not is_deleted:
            raise RatingNotFound(user_id, movielens_id)