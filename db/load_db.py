import sys
from pathlib import Path
import sqlite3


class DatabaseManager:
    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or Path(__file__).parent.parent / "data" / "clean" / "movies.db"

    def load_db(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn