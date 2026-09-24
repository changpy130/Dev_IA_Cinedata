import sqlite3
from pathlib import Path
import sys

ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT))

from src.csv_loader import load_movies

#region SQL requests
INSERT_MOVIE = """
    INSERT OR IGNORE INTO movies (movielens_id, title, year) VALUES (?, ?, ?)
"""


class MovieImporter:
    def run(self, conn: sqlite3.Connection) -> None:
        movies = load_movies()
        data = list(movies.itertuples(index=False, name=None))
        
        conn.executemany(
            INSERT_MOVIE, 
            data
        )
        conn.commit()


#region Test
if __name__ == "__main__":
    DB_PATH = Path(__file__).parent.parent.parent / "data" / "clean" / "movies.db"
    conn = sqlite3.connect(DB_PATH)
    movie_importer = MovieImporter()
    movie_importer.run(conn)
    conn.close()