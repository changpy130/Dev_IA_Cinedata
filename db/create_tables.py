import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "clean" / "movies.db"
SCHEMA_PATH = Path(__file__).parent / "sql" / "schema.sql"

def create_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")  # to enforce SQLite to use foreign key constraint
    
    sql = SCHEMA_PATH.read_text()
    conn.executescript(sql)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()