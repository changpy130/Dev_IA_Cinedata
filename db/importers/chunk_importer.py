import sys
import sqlite3
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT))

from domain.chunking import Chunk, chunk_plot

#region SQL
PLACEHOLDER = "No plot available"

LOAD = """
    SELECT d.movielens_id, d.plot
        FROM movie_details d
    LEFT JOIN plot_chunks c 
        ON c.movielens_id = d.movielens_id
    WHERE c.movielens_id IS NULL
    AND d.plot IS NOT NULL
    AND d.plot != ?
"""

INSERT = """
    INSERT OR IGNORE INTO plot_chunks (movielens_id, chunk_index, text)
    VALUES (?, ?, ?)
"""

class ChunkImporter:
    def __init__(self, batch_size: int = 500):
        """
        Args:
            batch_size (int, optional): Commit into DB after X movies. Defaults to 500.
        """
        self._batch_size = batch_size

    def run(self, conn: sqlite3.Connection) -> None:
        items = self._load_plots(conn)

        for start in range(0, len(items), self._batch_size):
            batch = items[start:start + self._batch_size]
            chunks = [ chunk_plot(movielens_id=movielens_id, plot=plot) for movielens_id, plot in batch ]
            flat_chunks = [ chunk for movie_chunks in chunks for chunk in movie_chunks ]
            self._insert(conn, flat_chunks)


#region DB handling
    def _load_plots(self, conn: sqlite3.Connection) -> list[tuple]:
        cursor = conn.execute(
            LOAD,
            (PLACEHOLDER,)
        )
        return cursor.fetchall()

    def _insert(self, conn: sqlite3.Connection, chunks: list[Chunk]):
        rows = [
            (chunk.movielens_id, chunk.chunk_index, chunk.text)
            for chunk in chunks
        ]
        conn.executemany(
            INSERT,
            rows
        )
        conn.commit()

#region Test
if __name__ == "__main__":
    from infrastructure.load_db import DatabaseManager
    
    manager = DatabaseManager()
    conn = manager.load_db()

    importer = ChunkImporter()
    importer.run(conn)

    conn.close()