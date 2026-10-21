#!/usr/bin/python3

# For cron log
from datetime import datetime
print(f"=== ETL started at {datetime.now():%Y-%m-%d %H:%M:%S} ===", flush=True)

import sys
from pathlib import Path
import sqlite3

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))

from db.importers.base import Importer
from db.importers.movie_importer import MovieImporter
from db.importers.movie_details_importer import MovieDetailsImporter
from db.importers.info_importer import InfoImporter
from db.importers.credit_importer import CreditImporter
from db.importers.plot_importer import PlotImporter
from infrastructure.load_db import DatabaseManager

importers: list[Importer] = [
    MovieImporter(),
    MovieDetailsImporter(),
    InfoImporter(),
    CreditImporter(
        cast_num=5, 
        crew_jobs=['Director', 'Writer', 'Editor', 'Director of Photography', 'Original Music Composer']
    ),
    PlotImporter(timeout=5, max_concurrent=1)
]

movie_db_manager = DatabaseManager()
conn = movie_db_manager.load_db()

for importer in importers:
    importer.run(conn=conn)

conn.close()

print(f"=== ETL ended at {datetime.now():%Y-%m-%d %H:%M:%S} ===", flush=True)