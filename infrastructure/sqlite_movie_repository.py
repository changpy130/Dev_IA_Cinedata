import sqlite3
from datetime import date

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from domain.db_entities import Movie, MovieDetails, CastMember, CrewMember, MovieGenre, Rating, CoLikeCount

#region SQL

# r: Python reads '\' as it is, not escape
SEARCH_BY_TITLE = r"""
    SELECT movielens_id, title, year
    FROM movies
    WHERE title LIKE :pattern ESCAPE '\'
    ORDER BY (title LIKE :prefix ESCAPE '\') DESC, title
    LIMIT :limit
"""


# Inherit MovieRepository protocol
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
            "d.vote_average, d.tagline, d.plot, d.overview "
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

    def search_by_title(self, query: str, limit: int) -> list[Movie]:
        escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        rows = self._conn.execute(
            SEARCH_BY_TITLE,
            {"pattern": f"%{escaped}%", "prefix": f"{escaped}%", "limit": limit},
        ).fetchall()

        return [ Movie(**row) for row in rows ]

#region Cast, Crew and Genre
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

    def get_crew(self, movielens_id: int) -> list[CrewMember]:
        cursor = self._conn.execute(
            "SELECT p.person_id, p.name, c.job "
            "FROM links l "
            "JOIN crew c ON l.tmdb_id = c.tmdb_id "
            "JOIN people p ON c.person_id = p.person_id "
            "WHERE l.movielens_id = ? "
            "ORDER BY p.name",
            (movielens_id,)
        )
        rows = cursor.fetchall()
        return [ CrewMember(**row) for row in rows ]

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

#region Rating
    def upsert_rating(self, rating: Rating) -> None:
        self._conn.execute(
            "INSERT INTO ratings (user_id, movielens_id, rating) VALUES (?, ?, ?) "
            "ON CONFLICT (user_id, movielens_id) DO UPDATE SET rating = excluded.rating",
            (rating.user_id, rating.movielens_id, rating.rating)
        )
        self._conn.commit()

    def delete_rating(self, user_id: int, movielens_id: int) -> bool:
        cursor = self._conn.execute(
            "DELETE FROM ratings WHERE user_id = ? AND movielens_id = ?",
            (user_id, movielens_id)
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def count_likes(self, movielens_id: int, min_rating: float = 4.0) -> int:
        cursor = self._conn.execute(
            "SELECT COUNT(user_id) FROM ratings "
            "WHERE movielens_id = ? AND rating >= ?",
            (movielens_id, min_rating)
        )
        row = cursor.fetchone()
        return row[0]

    def get_co_like_counts(self, movielens_id: int, min_rating: float = 4.0) -> list[CoLikeCount]:
        cursor = self._conn.execute(
            "SELECT r2.movielens_id, "
            "COUNT(r2.user_id) AS co_likes, "
            "(SELECT COUNT(*) FROM ratings r3 "
            "WHERE r3.movielens_id = r2.movielens_id "
            "AND r3.rating >= :min_rating) AS likes "
            "FROM ratings r1 "
            "JOIN ratings r2 "
            "ON r1.user_id = r2.user_id "
            "AND r1.movielens_id != r2.movielens_id "
            "WHERE r1.movielens_id = :movielens_id "
            "AND r1.rating >= :min_rating "
            "AND r2.rating >= :min_rating "
            "GROUP BY r2.movielens_id",
            { "movielens_id": movielens_id, "min_rating": min_rating }
        )
        rows = cursor.fetchall()
        return [ CoLikeCount(**row) for row in rows ]

#region Testing
if __name__ == "__main__":
    from infrastructure.load_db import DatabaseManager
    from collections import Counter
    conn = DatabaseManager().load_db()
    conn.row_factory = sqlite3.Row
    repo = SqliteMovieRepository(conn)

    conn.close()