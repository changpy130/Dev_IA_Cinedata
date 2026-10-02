import os
import requests
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio
import httpx

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from model.movie import PopularMoviesResponse, MoviewDetails, Credit, Cast, Crew


class TMDBExtractor(BaseModel):
    token: str
    base_url: str
    language: str = "en-UK"

    def __init__(self,**data):
        load_dotenv()
        data.setdefault("token", os.getenv("TMDB_TOKEN"))
        data.setdefault("base_url", os.getenv("TMDB_BASE_URL"))
        super().__init__(**data)


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
        credit.cast = self._select_cast(credit.cast, cast_num=cast_num)
        credit.crew = self._select_crew(credit.crew, crew_jobs=crew_jobs)

        return credit


    def get_genre_mapping(self):
        url = f"{self.base_url}/genre/movie/list"
        genre = self._parse_response(url)
        return { g['id']:g['name'] for g in genre['genres'] }


#region Async API
    async def _get_movie_details_async(self, client: httpx.AsyncClient, movie_id):
        if movie_id is None or movie_id == "":
            print("Movie ID is not valid!")
            return
        
        url = f"{self.base_url}/movie/{movie_id}"
        response = await self._parse_response_async(client, url)

        return MoviewDetails.model_validate(response) if response else None


    async def get_movie_details_list(self, movie_ids: list[int], max_concurrent: int = 20):
        semaphore = asyncio.Semaphore(max_concurrent)  # set the concurrent limit

        async def bounded_fetch(client, movie_id):
            async with semaphore:  # semaphore -> controls who gets to go and who needs to wait
                return await self._get_movie_details_async(client, movie_id)

        async with httpx.AsyncClient() as client:
            tasks = [ bounded_fetch(client, id) for id in movie_ids ]  # make a list of API-callings
            results = await asyncio.gather(*tasks)  # actually call APIs

        return [ result for result in results if result is not None ]


    async def _get_movie_credits_async(self, client: httpx.AsyncClient, movie_id: int, cast_num=5, crew_jobs=("Director",)) -> Credit | None:
        """Private function to call movie credit API by using async client.

        Args:
            client (httpx.AsyncClient)
            movie_id (int)
            cast_num (int, optional): Number of cast returned. Defaults to 5.
            crew_jobs (tuple, optional): Selected jobs returned. Defaults to ("Director",).

        Returns:
            Credit | None
        """
        url = f"{self.base_url}/movie/{movie_id}/credits"
        response = await self._parse_response_async(client, url)
        
        if response is None:
            return None

        credit = Credit.model_validate(response)
        credit.cast = self._select_cast(credit.cast, cast_num=cast_num)
        credit.crew = self._select_crew(credit.crew, crew_jobs=crew_jobs)
        return credit


    async def get_movie_credits_list(self, movie_ids: list[int], cast_num=5, crew_jobs=("Director",), max_concurrent: int = 20):
        """Entry point of getting movie credits by chunk, with asyncio.Semaphore and async client.

        Args:
            movie_ids (list[int]): a list of TMDB IDs
            cast_num (int, optional): Number of cast returned. Defaults to 5.
            crew_jobs (tuple, optional): Selected jobs returned. Defaults to ("Director",).
            max_concurrent (int, optional): Limit of concurrent API calls. Defaults to 20.

        Returns:
            results: A list of Credit or None.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def bounded_fetch(client, movie_id):
            async with semaphore:
                return await self._get_movie_credits_async(client=client, movie_id=movie_id, cast_num=cast_num, crew_jobs=crew_jobs)

        async with httpx.AsyncClient() as client:
            tasks = [ bounded_fetch(client, id) for id in movie_ids ]
            results = await asyncio.gather(*tasks)

        return [ result for result in results if result is not None ]


#region Data handling
    def _select_cast(self, cast_list: list[Cast], cast_num=5) -> list[Cast]:
        return cast_list[:cast_num]

    def _select_crew(self, crew_list: list[Crew], crew_jobs=("Director",)) -> list[Crew]:
        return [ person for person in crew_list if person.job in crew_jobs ]
            
#region Checking
    def _check_base_url(self):
        return bool(self.base_url)

    def _check_token(self):
        return bool(self.token)

    def check_auth(self):
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

    async def _parse_response_async(self, client: httpx.AsyncClient, url, params=None, timeout=5):
        """Call and parse response by async client

        Args:
            client (httpx.AsyncClient)
            url (str)
            params (_type_, optional): Defaults to None.
            timeout (int, optional): Defaults to 5.

        Returns:
            result: json or None
        """
        header = self._get_header()

        if params is None:
            params = self._get_params()

        try:
            response = await client.get(url, headers=header, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        
        except httpx.TimeoutException:
            print("Timeout: TMDB took too long to respond")
            return None

        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e}")
            return None

        except httpx.RequestError as e:
            print(f"Request error: {e}")
            return None


#region Main (testing)
if __name__ == "__main__":
    extractor = TMDBExtractor()

    if extractor.check_auth():
        ids = [862, 8844, 15602]
        credits = asyncio.run(extractor.get_movie_credits_list(ids, cast_num=5, crew_jobs=['Director', 'Writer']))

        for credit in credits:
            print(f"Cast: {credit.cast}")
            print(f"Crew: {credit.crew}")

    else:
        print("Configuration error.")