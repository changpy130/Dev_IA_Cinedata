import sys
from pathlib import Path
import sqlite3
import asyncio

ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT))

from src.wikipediaScraper import WikipediaScraper
from model.movie import WikiScrap
from db.load_db import DatabaseManager


#region SQL
LOAD = """
    SELECT m.movielens_id, m.title
    FROM movies m
    LEFT JOIN movie_details d
        ON m.movielens_id = d.movielens_id
    WHERE d.plot IS NULL
"""

UPDATE = """
    UPDATE movie_details
    SET plot = ?
    WHERE movielens_id = ?
"""

class PlotImporter:
    def __init__(self, timeout: int = 5, max_concurrent: int = 1):
        self.wikiscraper = WikipediaScraper(timeout, max_concurrent=max_concurrent)
    
    def run(self, conn: sqlite3.Connection) -> None:
        pairs = self._load(conn)
        plots = self.fetch_plot(pairs)
        self._insert(conn=conn, plots=plots)


    def fetch_plot(self, pairs: list[tuple]):
        return asyncio.run(
            self.wikiscraper.fetch_scrap_list(id_title_pairs=pairs)
        )


#region DB handling
    def _load(self, conn: sqlite3.Connection):
        cursor = conn.execute(LOAD)
        return cursor.fetchall() 


    def _insert(self, conn: sqlite3.Connection, plots: list[WikiScrap]):
        update_list = []

        for scrap in plots:
            scrap_insert = (
                scrap.plot,
                scrap.id
            )
            update_list.append(scrap_insert)

        conn.executemany(
            UPDATE,
            update_list
        )
        conn.commit()

#region Testing
if __name__ == "__main__":
    plot_importer = PlotImporter()
    manager = DatabaseManager()
    conn = manager.load_db()
    plot_importer.run(conn)
    conn.close()