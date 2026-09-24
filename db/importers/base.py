import sqlite3
from typing import Protocol

class Importer(Protocol):
    def run(self, conn: sqlite3.Connection) -> None:
        ...

