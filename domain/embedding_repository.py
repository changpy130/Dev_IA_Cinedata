from typing import Protocol

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from domain.embedding_index import EmbeddingIndex

class EmbeddingRepository(Protocol):
    def load_index(self, model_name: str) -> EmbeddingIndex: ...