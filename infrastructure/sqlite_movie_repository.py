import sqlite3

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from domain.db_entities import Movie


class SqliteMovieRepository:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def get_by_id(self, movielens_id: int) -> Movie | None:
        cursor = self._conn.execute(
            "SELECT movielens_id, title, year FROM movies WHERE movielens_id = ?",
            (movielens_id,)
        )
        row = cursor.fetchone()
        return Movie(**row) if row else None  # requires "conn.row_factory = sqlite3.Row" when setup to do "Movie(**row)"


#region Testing
if __name__ == "__main__":
    from infrastructure.load_db import DatabaseManager

    conn = DatabaseManager().load_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(
        "SELECT movielens_id, title, year FROM movies WHERE movielens_id = ?",
        (1,)
    )
    row = cursor.fetchone()
    print(Movie(**row) if row else None)