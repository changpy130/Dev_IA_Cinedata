import sqlite3
import numpy as np

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from domain.db_entities import PlotPassage

#region SQL
SEARCH_TEXT = """
    SELECT pc.movielens_id, pc.chunk_index, m.title, m.year, pc.text
    FROM plot_chunks pc
    JOIN movies m ON m.movielens_id = pc.movielens_id
    WHERE (pc.movielens_id, pc.chunk_index) IN (VALUES {placeholders})
"""

class SqliteChunkRepository:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
    
    def get_passages(self, keys: list[tuple[int, int]]) -> list[PlotPassage]:
        if not keys:
            return []
        
        placeholders = ", ".join(["(?, ?)"] * len(keys)) 
        params = [value for key in keys for value in key]

        rows = self._conn.execute(
            SEARCH_TEXT.format(placeholders=placeholders),
            params
        ).fetchall()

        results = [ PlotPassage(**row) for row in rows ]

        by_key = {
            (result.movielens_id, result.chunk_index): result
            for result in results
        }
        return [ by_key[key] for key in keys ]

#region Test
if __name__ == "__main__":
    from infrastructure.load_db import DatabaseManager
    conn = DatabaseManager().load_db()
    conn.row_factory = sqlite3.Row
    repo = SqliteChunkRepository(conn)

    results = repo.get_passages(
        keys=[(1, 1), (1, 2)]
    )
    print(results)

