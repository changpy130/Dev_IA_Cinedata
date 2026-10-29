import sys
import sqlite3
import numpy as np
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT))

from domain.embedder import Embedder
from domain.embedding_text import build_embedding_text

#region SQL
LOAD_MOVIES = """
SELECT 
    m.movielens_id, 
    m.title, 
    m.year, 
    d.overview, 
    d.tagline,
    GROUP_CONCAT(g.genre_name, ', ') AS genres
FROM movies m
JOIN movie_details d ON d.movielens_id = m.movielens_id
JOIN links l         ON l.movielens_id = m.movielens_id
LEFT JOIN movie_genres mg ON mg.tmdb_id = l.tmdb_id
LEFT JOIN genres g        ON g.genre_id = mg.genre_id
LEFT JOIN movie_embeddings e ON e.movielens_id = m.movielens_id AND e.model = ?
WHERE e.movielens_id IS NULL
GROUP BY m.movielens_id
"""

INSERT_EMBEDDING = """
    INSERT OR IGNORE INTO movie_embeddings (movielens_id, model, vector)
    VALUES (?, ?, ?)
"""


class EmbeddingImporter:
    def __init__(self, embedder: Embedder, batch_size: int = 64):
        self._embedder = embedder
        self._batch_size = batch_size
        
    def run(self, conn: sqlite3.Connection, limit: int | None) -> None:
        rows = self._load_movies(conn)[:limit]
        items = self._build_items(rows)

        # Making batches -> commit after each batch; if execution fails, only 64 movies are affected.
        for start in range(0, len(items), self._batch_size):
            batch = items[start:start + self._batch_size]
            self._embed_and_insert(batch, conn)


#region DB handling
    def _load_movies(self, conn: sqlite3.Connection) -> list[tuple]:
        return conn.execute(LOAD_MOVIES, (self._embedder.model_name,)).fetchall()

    def _build_items(self, rows: list[tuple]) -> list[tuple[int, str]]:
        items = []

        for movielens_id, title, year, overview, tagline, genres in rows:
            text = build_embedding_text(
                title=title,
                year=year,
                genres=genres,
                overview=overview,
                tagline=tagline
            )
            if text is not None:
                items.append((movielens_id, text))

        return items

    def _embed_and_insert(self, batch: list[tuple[int, str]], conn: sqlite3.Connection) -> None:
        ids = [ id for id, _ in batch ]
        texts = [ text for _, text in batch ]

        vectors = self._embedder.embed(texts)

        rows = [
            (movielens_id, self._embedder.model_name, vector.astype(np.float32).tobytes())
            for movielens_id, vector in zip(ids, vectors)
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

    importer = EmbeddingImporter(SentenceTransformerEmbedder())
    importer.run(conn, 20)
    conn.close()