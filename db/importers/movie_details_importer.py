import sys
import sqlite3
from pathlib import Path
import asyncio

ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT))

from src.TMDBExtractor import TMDBExtractor
from model.movie import MoviewDetails


#region SQL
LOAD_ID = """
    SELECT l.movielens_id, l.tmdb_id
    FROM links l
    LEFT JOIN movie_details d
        ON l.movielens_id = d.movielens_id
    WHERE d.movielens_id IS NULL
"""

INSERT_MOVIE_DETAILS = """
    INSERT OR IGNORE INTO movie_details (movielens_id, release_date, budget, revenue, runtime, vote_average, tagline)
    VALUES (?, ?, ?, ?, ?, ?, ?)
"""

INSERT_MOVIE_GENRES = """
    INSERT OR IGNORE INTO movie_genres (tmdb_id, genre_id)
    VALUES (?, ?)
"""


class MovieDetailsImporter:
    def __init__(self):
        self.extractor = TMDBExtractor()


    def run(self, conn: sqlite3.Connection) -> None:
        id_pairs = self._load_id(conn)
        tmdb_ids = [ item[1] for item in id_pairs ]
        movies = self._get_details(tmdb_ids)
        self._insert(id_pairs, movies, conn)


    def _get_details(self, ids: list[int]) -> list[MoviewDetails]:
        if not self.extractor.check_auth():
            return []
        return asyncio.run(self.extractor.get_movie_details_list(ids))


#region DB handling
    def _load_id(self, conn: sqlite3.Connection) -> list[tuple]:
        cursor = conn.execute(LOAD_ID)
        return cursor.fetchall()
    

    def _insert(self, id_pairs, movies: list[MoviewDetails], conn: sqlite3.Connection):
        id_mapping = self._id_mapping(id_pairs)
        details = []
        genres = []

        for movie in movies:
            movielens_id = id_mapping.get(movie.id)
            if movielens_id is None:
                print(f"No match ID for {movie.id} {movie.title}")
                continue

            detail = (
                movielens_id,
                movie.release_date, 
                movie.budget, 
                movie.revenue, 
                movie.runtime, 
                movie.vote_average, 
                movie.tagline
            )
            details.append(detail)

            for genre in movie.genres:
                genre_detail = (movie.id, genre.id)
                genres.append(genre_detail)

        conn.executemany(
            INSERT_MOVIE_DETAILS,
            details
        )
        conn.executemany(
            INSERT_MOVIE_GENRES,
            genres
        )
        conn.commit()
        

#region Utility
    def _id_mapping(self, id_pairs):
        return { tmdb_id: movielens_id for movielens_id, tmdb_id in id_pairs }

if __name__ == "__main__":
    DB_PATH = Path(__file__).parent.parent.parent / "data" / "clean" / "movies.db"
    conn = sqlite3.connect(DB_PATH)
    importer = MovieDetailsImporter()
    importer.run(conn)
    conn.close()