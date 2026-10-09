from typing import Protocol

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from domain.db_entities import Movie

class MovieRepository(Protocol):
    def get_by_id(self, movielens_id: int) -> Movie | None: ...