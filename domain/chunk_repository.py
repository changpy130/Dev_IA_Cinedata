from typing import Protocol

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from domain.db_entities import PlotPassage

class ChunkRepository(Protocol):
    def get_passages(self, keys: list[tuple[int, int]]) -> list[PlotPassage]: ...