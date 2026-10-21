import numpy as np
from sentence_transformers import SentenceTransformer

class SentenceTransformerEmbedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> np.ndarray:
        """Make a list of text into a list of vectors

        Args:
            texts (list[str]): A list of input text, ex: a list of movie infos

        Returns:
            np.ndarray: vectors
        """
        return self._model.encode(texts, normalize_embeddings=True)