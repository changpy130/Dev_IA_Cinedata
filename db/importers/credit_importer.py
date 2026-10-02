import sys
import sqlite3
from pathlib import Path
import asyncio

ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT))

from src.TMDBExtractor import TMDBExtractor
from db.load_db import DatabaseManager
from model.movie import Credit, Cast, Crew

#region SQL
LOAD_ID = """
    SELECT l.tmdb_id
    FROM links l
    LEFT JOIN movie_cast c
        ON l.tmdb_id = c.tmdb_id
    WHERE c.tmdb_id IS NULL
"""

INSERT_PEOPLE = """
    INSERT OR IGNORE INTO people (person_id, name)
    VALUES (?, ?)
"""

INSERT_CAST = """
    INSERT OR IGNORE INTO movie_cast (tmdb_id, person_id, character)
    VALUES (?, ?, ?)
"""

INSERT_CREW = """
    INSERT OR IGNORE INTO crew (tmdb_id, person_id, job)
    VALUES (?, ?, ?)
"""



class CreditImporter:
    def __init__(self, cast_num=5, crew_jobs=('Director',)):
        self.extractor = TMDBExtractor()
        self.cast_num = cast_num
        self.crew_jobs = crew_jobs

    def run(self, conn: sqlite3.Connection) -> None:
        ids = self._load_id(conn)
        credits = self._get_credits(ids)
        self._insert(credits=credits, conn=conn)


    def _get_credits(self, ids: list[int]) -> list[Credit]:
        if not self.extractor.check_auth():
            return []
        return asyncio.run(
            self.extractor.get_movie_credits_list(
                ids, 
                cast_num=self.cast_num, 
                crew_jobs=self.crew_jobs,
                max_concurrent=20
            )
        )

#region DB handling
    def _load_id(self, conn: sqlite3.Connection) -> list[int]:
        cursor = conn.execute(LOAD_ID)
        return [ row[0] for row in cursor.fetchall() ]

    def _insert(self, credits: list[Credit], conn: sqlite3.Connection):
        people = []
        cast_list = []
        crew_list = []

        for credit in credits:
            for cast in credit.cast:
                person = (
                    cast.id,
                    cast.name
                )
                cast_insert = (
                    credit.id,
                    cast.id,
                    cast.character
                )
                people.append(person)
                cast_list.append(cast_insert)

            for member in credit.crew:
                person = (
                    member.id,
                    member.name
                )
                crew_insert = (
                    credit.id,
                    member.id,
                    member.job
                )
                people.append(person)
                crew_list.append(crew_insert)

        conn.executemany(
            INSERT_PEOPLE,
            people
        )
        conn.executemany(
            INSERT_CAST,
            cast_list
        )
        conn.executemany(
            INSERT_CREW,
            crew_list
        )
        conn.commit()

#region Test
if __name__ == "__main__":
    db_manager = DatabaseManager()
    conn = db_manager.load_db()

    importer = CreditImporter()
    importer.run(conn)
    conn.close()