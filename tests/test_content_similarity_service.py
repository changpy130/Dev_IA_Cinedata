import numpy as np
import pytest

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from domain.embedding_index import EmbeddingIndex
from domain.db_entities import Movie, MovieDetails
from tests.fakes import FakeMovieRepository
from services.movie_service import EmbeddingNotFound, MovieNotFound, MovieService
from services.content_similarity_service import ContentSimilarityService

@pytest.fixture
def index():
    matrix = np.array([
        [1.0, 0.0],
        [0.8, 0.6],
        [0.0, 1.0],
    ], dtype=np.float32)
    return EmbeddingIndex([10, 20, 30], matrix)

@pytest.fixture
def repo():
    return FakeMovieRepository(
        movies=[
            Movie(movielens_id=10, title="10", year=2011),
            Movie(movielens_id=20, title="20", year=2011),
            Movie(movielens_id=30, title="30", year=2011),
            Movie(movielens_id=40, title="40", year=2011)
        ],
        details=[
            MovieDetails(movielens_id=10, title="MD10", year=2000, release_date=None, budget=None, revenue=None, runtime=None, vote_average=None, tagline="HELLLOOOO10", plot=None, overview=""),
            MovieDetails(movielens_id=20, title="MD20", year=2013, release_date=None, budget=None, revenue=None, runtime=None, vote_average=None, tagline="HELLLOOOO20", plot=None, overview=""),
            MovieDetails(movielens_id=30, title="MD30", year=2011, release_date=None, budget=None, revenue=None, runtime=None, vote_average=None, tagline="HELLLOOOO30", plot=None, overview=""),
            MovieDetails(movielens_id=40, title="MD40", year=2011, release_date=None, budget=None, revenue=None, runtime=None, vote_average=None, tagline="HELLLOOOO40", plot=None, overview=""),
        ]
    )

@pytest.fixture
def service(repo, index):
    return ContentSimilarityService(
        movie_service=MovieService(repo=repo),
        index=index
    )

def test_get_similar_by_content(service):
    movies = service.get_similar_by_content(10, limit=2)
    assert [ movie.movielens_id for movie in movies ] == [20, 30]

def test_unknown_movie(service):
    with pytest.raises(MovieNotFound):
        service.get_similar_by_content(movielens_id=1, limit=2)

def test_no_embedding(service):
    with pytest.raises(EmbeddingNotFound):
        service.get_similar_by_content(40, limit=2)

def test_ranking(service):
    results = service.get_similar_by_content(10, limit=1)
    assert [r.movielens_id for r in results] == [20]