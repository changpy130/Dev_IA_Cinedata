import numpy as np

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

class ChunkIndex:
    def __init__(self, keys: list[tuple[int, int]], matrix: np.ndarray):
        if len(keys) != matrix.shape[0]:
            raise ValueError(f"{len(keys)} keys but {matrix.shape[0]} matrix rows")
        
        self._keys = keys
        self._matrix = matrix

    def most_similar(self, query_vector: np.ndarray, limit: int) -> list[tuple[int, int, float]]:
        scores = self._matrix @ query_vector
        best_rows = np.argsort(scores)[::-1][:limit] 

        return [ (*self._keys[i], float(scores[i])) for i in best_rows ]