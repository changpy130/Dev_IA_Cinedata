import sqlite3
from pathlib import Path
import sys

ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT))

from src.csv_loader import load_links, load_ratings, load_genres

#region SQL requests
INSERT_LINKS = """
    INSERT OR IGNORE INTO links (movielens_id, tmdb_id, imdb_id) VALUES (?, ?, ?)
"""

INSERT_RATINGS = """
    INSERT OR IGNORE INTO ratings (user_id, movielens_id, rating) VALUES (?, ?, ?)
"""

INSERT_GENRES = """
    INSERT OR IGNORE INTO genres (genre_id, genre_name) VALUES (?, ?)
"""


class InfoImporter:
    def run(self, conn: sqlite3.Connection) -> None:
        links = load_links()
        links_data = list(links.itertuples(index=False, name=None))
        
        genres = load_genres()
        genres_data = list(genres.itertuples(index=False, name=None))
        
        ratings = load_ratings()
        ratings_data = list(ratings.itertuples(index=False, name=None))

        self.execute_sql(conn, INSERT_LINKS, links_data)
        self.execute_sql(conn, INSERT_RATINGS, ratings_data)
        self.execute_sql(conn, INSERT_GENRES, genres_data)


    def execute_sql(self, conn: sqlite3.Connection, sql, data):
        conn.executemany(
            sql, 
            data
        )
        conn.commit()


#region Test
if __name__ == "__main__":
    DB_PATH = Path(__file__).parent.parent.parent / "data" / "clean" / "movies.db"
    conn = sqlite3.connect(DB_PATH)
    infoimporter = InfoImporter()
    infoimporter.run(conn)
    conn.close()