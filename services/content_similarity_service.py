import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from domain.db_entities import SimilarMovie, SimilarMovieDetails
from domain.embedding_index import EmbeddingIndex
from services.movie_service import MovieService, MovieDetailsNotFound, EmbeddingNotFound

class ContentSimilarityService:
    def __init__(self, movie_service: MovieService, index: EmbeddingIndex):
        self._movie_service = movie_service
        self._index = index

    def get_similar_by_content(self, movielens_id: int, limit: int = 5) -> list[SimilarMovie]:
        self._movie_service.get_movie(movielens_id)

        if not self._index.has(movielens_id):
            raise EmbeddingNotFound(movielens_id)

        return self._index.most_similar(movielens_id, limit)

    def get_similar_by_content_with_details(self, movielens_id: int, limit: int = 5) -> list[SimilarMovieDetails]:
        result: list[SimilarMovieDetails] = []

        for similar in self.get_similar_by_content(movielens_id, limit):
            try:
                details = self._movie_service.get_details(similar.movielens_id)
            except MovieDetailsNotFound:
                continue
            result.append(SimilarMovieDetails(details, similar.score))

        return result