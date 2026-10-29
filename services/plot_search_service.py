import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from domain.chunk_index import ChunkIndex
from domain.embedder import Embedder

class PlotSearchService:
    def __init__(self, embedder: Embedder, index: ChunkIndex):
        self._embedder = embedder
        self._index = index

    def search(self, question: str, limit: int = 5) -> list[tuple[int, int, float]]:
        """Search the most similar passages from the question

        Args:
            question (str): Text to search
            limit (int, optional): Numbers of returned movies. Defaults to 5.

        Returns:
            list[tuple[int, int, float]]: (movielens_id, chunk_index, score)
        """
        vector = self._embedder.embed(texts=[question])[0]
        return self._index.most_similar(query_vector=vector, limit=limit)