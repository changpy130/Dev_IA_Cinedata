# Purpose: Calculate the "score"(similarity) from matrix and find the highest score

import numpy as np

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from domain.db_entities import SimilarMovie

class EmbeddingIndex:
    def __init__(self, movielens_ids: list[int], matrix: np.ndarray):
        self._ids = movielens_ids
        self._matrix = matrix
        self._position = { id: row for row, id in enumerate(movielens_ids) }

    def has(self, id: int) -> bool:
        return id in self._position

    def most_similar(self, id: int, limit: int) -> list[SimilarMovie]:
        row = self._position.get(id)
        scores = self._matrix @ self._matrix[row]
        scores[row] = -1.0

        best_rows = np.argsort(scores)[::-1][:limit]  #return an array of the index
        return [ SimilarMovie(movielens_id=self._ids[i], score=float(scores[i])) for i in best_rows ]
