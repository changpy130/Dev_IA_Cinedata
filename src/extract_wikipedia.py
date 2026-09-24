import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from wikipediaScraper import WikipediaScraper

scraper = WikipediaScraper()

