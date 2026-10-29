import numpy as np
import sys
import sqlite3
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT))

from domain.embedder import Embedder
from domain.embedding_text import build_chunk_embedding_text

#region SQL
LOAD = """
    SELECT 
        c.movielens_id, 
        c.chunk_index, 
        c.text, 
        m.title, 
        m.year
    FROM plot_chunks c
    JOIN movies m 
        ON m.movielens_id = c.movielens_id
    LEFT JOIN chunk_embeddings e
        ON e.movielens_id = c.movielens_id
    AND e.chunk_index = c.chunk_index
    AND e.model = ?
    WHERE e.movielens_id IS NULL
"""

INSERT_EMBEDDING = """
    INSERT OR IGNORE INTO chunk_embeddings (movielens_id, chunk_index, model, vector)
    VALUES (?, ?, ?, ?)
"""

class ChunkEmbeddingImporter:
    def __init__(self, embedder: Embedder, batch_size: int = 64):
        self._embedder = embedder
        self._batch_size = batch_size
    
    def run(self, conn: sqlite3.Connection) -> None:
        rows = self._load(conn)
        items = self._build_items(rows)

        for start in range(0, len(items), self._batch_size):
            batch = items[start: start + self._batch_size]
            self._embed_and_insert(batch, conn)


#region Helpers
    def _build_items(self, rows: list[tuple]) -> list[tuple]:
        items = [
            (
                movielens_id,
                chunk_index,
                build_chunk_embedding_text(
                    title=title,
                    year=year,
                    chunk_text=chunk_text
                )
            )
            for movielens_id, chunk_index, chunk_text, title, year in rows
        ]
        return items

#region DB handling
    def _load(self, conn: sqlite3.Connection) -> list[tuple]:
        return conn.execute(LOAD, (self._embedder.model_name,)).fetchall()

    def _embed_and_insert(self, batch: list[tuple], conn: sqlite3.Connection) -> None:
        """Embed the chunk texts and insert into DB

        Args:
            batch (list[tuple]): shaped (movielens_id, chunk_index, text)
            conn (sqlite3.Connection)
        """
        texts = [ text for _, _, text in batch ]
        vectors = self._embedder.embed(texts)

        assert len(vectors) == len(batch), "embedder returned a different number of vectors"

        rows = [
            (movielens_id, chunk_index, self._embedder.model_name, vector.astype(np.float32).tobytes())
            for (movielens_id, chunk_index, _), vector in zip(batch, vectors)
        ]

        conn.executemany(
            INSERT_EMBEDDING,
            rows
        )
        conn.commit()

#region Test
if __name__ == "__main__":
    from infrastructure.load_db import DatabaseManager
    from infrastructure.sentence_transformer_embedder import SentenceTransformerEmbedder
    
    manager = DatabaseManager()
    conn = manager.load_db()

    importer = ChunkEmbeddingImporter(SentenceTransformerEmbedder(), batch_size=64)
    importer.run(conn)

    conn.close()