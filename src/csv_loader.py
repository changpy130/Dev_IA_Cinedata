import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent.parent

def load_movies():
    return pd.read_csv(ROOT / "data" / "clean" / "movies.csv")

def load_links():
    return pd.read_csv(ROOT / "data" / "clean" / "links.csv")

def load_genres():
    return pd.read_csv(ROOT / "data" / "clean" / "genres.csv")

def load_ratings():
    return pd.read_csv(ROOT / "data" / "clean" / "ratings.csv")