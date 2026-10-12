import sqlite3
from datetime import date

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from domain.db_entities import Movie, MovieDetails, CastMember, MovieGenre


class SqliteMovieRepository:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def get_by_id(self, movielens_id: int) -> Movie | None:
        cursor = self._conn.execute(
            "SELECT movielens_id, title, year FROM movies WHERE movielens_id = ?",
            (movielens_id,)  # parametre needs to be a tuple for SQL
        )
        row = cursor.fetchone()
        return Movie(**row) if row else None  # requires "conn.row_factory = sqlite3.Row" when setup to do "Movie(**row)"

    def list_movies(self, limit: int, offset: int, year: int | None = None, genre: str | None = None) -> list[Movie]:
        query = "SELECT m.movielens_id, m.title, m.year FROM movies m"
        params: list[int | str] = []
        conditions: list[str] = []

        if genre is not None:
            query += (
                " JOIN links l ON m.movielens_id = l.movielens_id"
                " JOIN movie_genres mg ON l.tmdb_id = mg.tmdb_id"
                " JOIN genres g ON mg.genre_id = g.genre_id"
            )
            params.append(genre)
            conditions.append("g.genre_name = ?")

        if year is not None:
            params.append(year)
            conditions.append("m.year = ?")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY m.movielens_id LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = self._conn.execute(
            query,
            params
        )
        rows = cursor.fetchall()
        return [ Movie(**row) for row in rows ]

    def get_details(self, movielens_id: int) -> MovieDetails | None: 
        cursor = self._conn.execute(
            "SELECT m.movielens_id, m.title, m.year, "
            "d.release_date, d.budget, d.revenue, d.runtime, "
            "d.vote_average, d.tagline, d.plot "
            "FROM movies m "
            "JOIN movie_details d ON m.movielens_id = d.movielens_id "
            "WHERE m.movielens_id = ?",
            (movielens_id,),
        )
        row = cursor.fetchone()

        if row is None:
            return None

        data = dict(row)  # copy row's value to modify (row is read-only object)
        if data['release_date'] is not None:
            raw = data['release_date']
            data['release_date'] = date.fromisoformat(raw) if raw else None
        
        return MovieDetails(**data)

    def get_cast(self, movielens_id: int) -> list[CastMember]:
        cursor = self._conn.execute(
            "SELECT p.person_id, p.name, mc.character "
            "FROM links l "
            "JOIN movie_cast mc ON l.tmdb_id = mc.tmdb_id "
            "JOIN people p ON mc.person_id = p.person_id "
            "WHERE l.movielens_id = ? "
            "ORDER BY p.name",
            (movielens_id,)
        )
        rows = cursor.fetchall()
        return [ CastMember(**row) for row in rows ]

    def get_genres(self, movielens_id: int) -> list[MovieGenre]:
        cursor = self._conn.execute(
            "SELECT g.genre_id, g.genre_name FROM links l "
            "JOIN movie_genres mg ON l.tmdb_id = mg.tmdb_id "
            "JOIN genres g ON mg.genre_id = g.genre_id "
            "WHERE l.movielens_id = ? "
            "ORDER BY g.genre_id",
            (movielens_id,)
        )
        rows = cursor.fetchall()
        return [ MovieGenre(**row) for row in rows ]


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