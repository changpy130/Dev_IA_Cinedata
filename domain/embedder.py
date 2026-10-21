from typing import Protocol
import numpy as np

class Embedder(Protocol):
    model_name: str

    def embed(self, texts: list[str]) -> np.ndarray:
        """Return one unit-length vector per text, shape (len(texts), dimensions)."""
        ...