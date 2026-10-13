import pytest
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from domain.db_entities import Movie
from services.movie_service import MovieService, MovieNotFound, RatingNotFound
from tests.fakes import FakeMovieRepository


def make_service(movies: list[Movie] | None = None) -> tuple[MovieService, FakeMovieRepository]:
    repo = FakeMovieRepository(movies)
    return MovieService(repo), repo


def test_get_movie_returns_movie_when_it_exists():
    movie = Movie(movielens_id=1, title="Toy Story", year=1995)
    service, _ = make_service([movie])

    assert service.get_movie(1) == movie


def test_get_movie_raises_when_missing():
    service, _ = make_service()

    with pytest.raises(MovieNotFound):
        service.get_movie(999)


def test_upsert_rating_rejects_unknown_movie():
    service, repo = make_service()

    with pytest.raises(MovieNotFound):
        service.upsert_rating(user_id=1, movielens_id=999, rating=4.5)

    assert repo._ratings == {}

def test_delete_rating_succeeds_when_rating_exists():
    service, repo = make_service([Movie(1, "Toy Story", 1995)])
    service.upsert_rating(user_id=1, movielens_id=1, rating=4.5)

    service.delete_rating(user_id=1, movielens_id=1)

    assert repo._ratings == {}


def test_delete_rating_raises_when_rating_missing():
    service, _ = make_service([Movie(1, "Toy Story", 1995)])

    with pytest.raises(RatingNotFound):
        service.delete_rating(user_id=1, movielens_id=1)