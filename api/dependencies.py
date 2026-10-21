import sqlite3
from fastapi import Depends, Request
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from infrastructure.database import get_connection
from infrastructure.sqlite_movie_repository import SqliteMovieRepository
from services.movie_service import MovieService

from domain.embedding_index import EmbeddingIndex
from services.content_similarity_service import ContentSimilarityService


def get_sqlite_movie_service(conn: sqlite3.Connection = Depends(get_connection)) -> MovieService:
    return MovieService(SqliteMovieRepository(conn))

def get_embedding_index(request: Request) -> EmbeddingIndex:
    return request.app.state.embedding_index

def get_content_similarity_service(
    movie_service: MovieService = Depends(get_sqlite_movie_service),
    index: EmbeddingIndex = Depends(get_embedding_index)
) -> ContentSimilarityService:
    return ContentSimilarityService(movie_service, index)