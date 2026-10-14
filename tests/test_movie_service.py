import pytest
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from domain.db_entities import Movie, MovieDetails, SimilarMovie
from services.movie_service import MovieService, MovieNotFound, RatingNotFound
from tests.fakes import FakeMovieRepository


def make_service(movies: list[Movie] | None = None, details: list[MovieDetails] | None = None) -> tuple[MovieService, FakeMovieRepository]:
    repo = FakeMovieRepository(movies, details)
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

def test_similar_movies_ranked_by_score_and_filtered():
    service, _ = make_service([Movie(1, "Toy Story", 1995)])
    result = service.get_similar_movies(movielens_id=1, min_co_likes=3)

    assert [s.movielens_id for s in result] == [30, 10]

def test_similar_movies_respects_limit():
    service, _ = make_service([Movie(1, "Toy Story", 1995)])
    result = service.get_similar_movies(movielens_id=1, min_co_likes=1, limit=1)

    assert [ s.movielens_id for s in result ] == [30]

def test_get_similar_movies_with_details():
    service, _ = make_service([ 
        Movie(movielens_id=1, title="Toy Story", year=1995)
    ], [
        MovieDetails(movielens_id=10, title="MD10", year=2000, release_date=None, budget=None, revenue=None, runtime=None, vote_average=None, tagline="HELLLOOOO10", plot=None),
        MovieDetails(movielens_id=30, title="MD30", year=2011, release_date=None, budget=None, revenue=None, runtime=None, vote_average=None, tagline="HELLLOOOO30", plot=None),
    ])
    result = service.get_similar_movies_with_details(movielens_id=1, min_co_likes=1)
    # should skip movielens_id=20 404 error from the fake data

    assert [ s.details.movielens_id for s in result ] == [30, 10]

    assert result[0].score == pytest.approx(8 / 12)