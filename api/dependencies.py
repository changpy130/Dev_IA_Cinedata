import sqlite3
from fastapi import Depends
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from infrastructure.database import get_connection
from infrastructure.sqlite_movie_repository import SqliteMovieRepository
from services.movie_service import MovieService


def get_sqlite_movie_service(conn: sqlite3.Connection = Depends(get_connection)) -> MovieService:
    return MovieService(SqliteMovieRepository(conn))