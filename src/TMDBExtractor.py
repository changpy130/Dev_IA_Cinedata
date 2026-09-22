import os
import requests
from pydantic import BaseModel
from dotenv import load_dotenv

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from model.movie import PopularMoviesResponse, MoviewDetails, Credit


class TMDBExtractor(BaseModel):
    token: str
    base_url: str
    language: str = "en-UK"
    genre_mapping: dict = {}

    def __init__(self,**data):
        load_dotenv()
        data.setdefault("token", os.getenv("TMDB_TOKEN"))
        data.setdefault("base_url", os.getenv("TMDB_BASE_URL"))
        super().__init__(**data)
        self._get_genre_mapping()


#region APIs
    def get_popular_movies(self, page=1):
        url = f"{self.base_url}/movie/popular"

        params = self._get_params()
        params['page'] = page

        response = self._parse_response(url, params)
        data = PopularMoviesResponse.model_validate(response)

        return data.results

    def get_movie_details(self, movie_id):
        if movie_id is None or movie_id == "":
            print("Movie ID is not valid!")
            return
        
        url = f"{self.base_url}/movie/{movie_id}"
        response = self._parse_response(url)

        return MoviewDetails.model_validate(response)

    def get_movie_credits(self, movie_id, cast_num=5, crew_jobs=("Director",)):
        url = f"{self.base_url}/movie/{movie_id}/credits"

        response = self._parse_response(url)
        credit = Credit.model_validate(response)
        credit.cast = credit.cast[:cast_num]
        credit.crew = [ person for person in credit.crew if person.job in crew_jobs ]

        return credit


    def _get_genre_mapping(self):
        url = f"{self.base_url}/genre/movie/list"
        genre = self._parse_response(url)
        self.genre_mapping = { g['id']:g['name'] for g in genre['genres'] }


#region Checking
    def _check_base_url(self):
        return bool(self.base_url)

    def _check_token(self):
        return bool(self.token)

    def _check_auth(self):
        return self._check_base_url() and self._check_token()


#region Utility
    def _get_header(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "accept": "application/json"
        }

    def _get_params(self):
        return {
            "language": self.language
        }

    def _parse_response(self, url, params=None, timeout=5):
        header = self._get_header()

        if params is None:
            params = self._get_params()

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

#region Main (testing)
if __name__ == "__main__":
    extractor = TMDBExtractor()

    if extractor._check_auth():
        movies = extractor.get_popular_movies()

        for movie in movies[:1]:
            details = extractor.get_movie_details(movie.id)
            credit = extractor.get_movie_credits(movie_id=movie.id)

            print(f"{movie.title}, directed by {credit.crew[0]}, tagline: {details.tagline}, main actors: {credit.cast}")

    else:
        print("Configuration error.")