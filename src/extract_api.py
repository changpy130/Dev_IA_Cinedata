import os
import requests
import pandas as pd
from dotenv import load_dotenv

#region Config
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = os.getenv("TMDB_BASE_URL")
TMDB_TOKEN = os.getenv("TMDB_TOKEN")


#region Checking
def check_auth():
    return check_api_key() and check_base_url() and check_token()

def check_api_key():
    return bool(TMDB_API_KEY)

def check_base_url():
    return bool(TMDB_BASE_URL)

def check_token():
    return bool(TMDB_TOKEN)

#region APIs
def get_header():
    return {
        "Authorization": f"Bearer {TMDB_TOKEN}",
        "accept": "application/json"
    }

def get_params():
    language = "en-UK"

    return {
        "language": language
    }

def parse_response(url, params=None, timeout=5):
    header = get_header()

    if params is None:
        params = get_params()

    try:
        response = requests.get(url, headers=header, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.Timeout:
        print("Timeout: TMDB took too long to respond")
        return None
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None


def get_popular_movies(page=1):
    url = f"{TMDB_BASE_URL}/movie/popular"

    params = get_params()
    params['page'] = page

    return parse_response(url, params)


def get_genre_mapping():
    url = f"{TMDB_BASE_URL}/genre/movie/list"

    return parse_response(url)


def get_movie_details(movie_id):
    if movie_id is None or movie_id == "":
        print("Movie ID is not valid!")
        return
    
    url = f"{TMDB_BASE_URL}/movie/{movie_id}"

    return parse_response(url)


def get_movie_cast(movie_id):
    url = f"{TMDB_BASE_URL}/movie/{movie_id}/credits"

    return parse_response(url)

#region Main
if __name__ == "__main__":
    if check_auth():
        data = get_genre_mapping()
        print(data)
    else:
        print("Config is not correctly read.")