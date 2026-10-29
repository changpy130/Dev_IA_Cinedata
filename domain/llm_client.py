from typing import Protocol

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

class LLMClient(Protocol):
    def complete(self, system: str, user: str) -> str: ...