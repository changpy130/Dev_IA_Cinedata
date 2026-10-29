import sys
from pathlib import Path
import sqlite3
import asyncio

ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT))

from src.wikipediaScraper import WikipediaScraper
from domain.tmdb_movies import WikiScrap
from infrastructure.load_db import DatabaseManager


#region SQL
LOAD = """
    SELECT m.movielens_id, m.title
    FROM movies m
    JOIN movie_details d 
        ON m.movielens_id = d.movielens_id
    LEFT JOIN plot_attempts a 
        ON m.movielens_id = a.movielens_id
    WHERE d.plot IS NULL
      AND a.movielens_id IS NULL
"""

LOAD_MISSING_PLOT = """
    SELECT m.movielens_id, m.title 
    FROM movies m 
    JOIN plot_attempts p 
        ON m.movielens_id = p.movielens_id
    JOIN movie_details d 
        ON m.movielens_id = d.movielens_id
    WHERE d.plot IS NULL
"""

UPDATE = """
    UPDATE movie_details
    SET plot = ?
    WHERE movielens_id = ?
"""

INSERT_NOT_FOUND = """
    INSERT OR IGNORE INTO plot_attempts (movielens_id, status)
    VALUES (?, 'not_found')
"""

class PlotImporter:
    def __init__(self, timeout: int = 5, max_concurrent: int = 1):
        self.wikiscraper = WikipediaScraper(timeout, max_concurrent=max_concurrent)
    
    def run(self, conn: sqlite3.Connection) -> None:
        pairs = self._load(conn)
        
        if not pairs:
            print("Plot scrapping has finished.")
            return
        
        results = self.fetch_plot(pairs)
        self._insert(conn=conn, results=results)


    def fetch_plot(self, pairs: list[tuple]):
        return asyncio.run(
            self.wikiscraper.fetch_scrap_list(id_title_pairs=pairs)
        )


#region DB handling
    def _load(self, conn: sqlite3.Connection):
        cursor = conn.execute(LOAD)
        return cursor.fetchall() 


    def _insert(self, conn: sqlite3.Connection, results: list[tuple]):
        found, not_found = [], []

        for movielens_id, scrap, failed in results:
            if failed:
                continue                              # transient: leave unlogged, retry next run
            if scrap is None:
                not_found.append((movielens_id,))     # permanent miss: log it
            else:
                found.append((scrap.plot, movielens_id))

        conn.executemany(
            UPDATE,
            found
        )
        conn.executemany(
            INSERT_NOT_FOUND,
            not_found
        )
        conn.commit()

#region Testing
if __name__ == "__main__":
    plot_importer = PlotImporter()
    manager = DatabaseManager()
    conn = manager.load_db()
    plot_importer.run(conn)
    conn.close()