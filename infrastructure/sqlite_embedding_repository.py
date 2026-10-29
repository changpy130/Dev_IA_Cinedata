import sqlite3
import numpy as np

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from domain.embedding_index import EmbeddingIndex
from domain.chunk_index import ChunkIndex

#region SQL
LOAD_VECTORS = """
    SELECT movielens_id, vector
    FROM movie_embeddings
    WHERE model = ?
    ORDER BY movielens_id
"""

LOAD_CHUNK = """
    SELECT e.movielens_id, e.chunk_index, e.vector
    FROM chunk_embeddings e
    WHERE e.model = ?
    ORDER BY e.movielens_id, e.chunk_index
"""


# Inherit EmbeddingRepository protocol
class SqliteEmbeddingRepository:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def load_index(self, model_name: str) -> EmbeddingIndex: 
        rows = self._conn.execute(LOAD_VECTORS, (model_name,)).fetchall()
        if not rows:
            raise ValueError(f"No embeddings stored for model '{model_name}'")

        ids = [ id for id, _ in rows ]
        matrix = np.vstack(
            [np.frombuffer(blob, dtype=np.float32) for _, blob in rows]  # bytes-to-vector conversion
        )
        return EmbeddingIndex(ids, matrix)

    def load_chunk_index(self, model_name: str) -> ChunkIndex:
        rows = self._conn.execute(LOAD_CHUNK, (model_name,)).fetchall()
        if not rows:
            raise ValueError(f"No chunk embeddings stored for model '{model_name}'")

        keys = [(movielens_id, chunk_index) for movielens_id, chunk_index, _ in rows]
        matrix = np.vstack(
            [np.frombuffer(r[2], dtype=np.float32) for r in rows]
        )
        return ChunkIndex(keys=keys, matrix=matrix)

#region Test
if __name__ == "__main__":
    from infrastructure.load_db import DatabaseManager
    conn = DatabaseManager().load_db()
    index = SqliteEmbeddingRepository(conn).load_index("all-MiniLM-L6-v2")

    for similar in index.most_similar(1, limit=5):   # 1 = Toy Story
        title = conn.execute(
            "SELECT title FROM movies WHERE movielens_id = ?", (similar.movielens_id,)
        ).fetchone()[0]
        print(round(similar.score, 3), title)