import sqlite3
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from infrastructure.load_db import DatabaseManager


def get_connection():
    conn = DatabaseManager().load_db()
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()