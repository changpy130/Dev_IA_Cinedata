import requests
from bs4 import BeautifulSoup
import httpx, asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from model.movie import WikiScrap


class WikipediaScraper:
    def __init__(self, timeout: int = 5, headers: dict = None, max_concurrent: int = 20):
        self.timeout = timeout
        self.headers = headers or {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        }
        self.max_concurrent = max_concurrent

#region Entry points
    def fetch_scrap(self, title):
        url = self._find_url(title)
        soup = self._get_soup(url)
        name = self._get_title(soup)
        infobox = self._get_infobox(soup)
        plot = self._get_plot(soup)

        scrap = {
            'title': name,
            'infobox': infobox,
            'plot': plot
        }
        return WikiScrap.model_validate(scrap)

    async def fetch_scrap_list(self, id_title_pairs: list[tuple]):
        """Async fetch Wikipedia scrapping

        Args:
            id_title_pairs (list[tuple]): (movielens_id, title)
            max_concurrent (int, optional): Maximum concurrent APIs. Defaults to 20.

        Returns:
            list: A list of WikiScrap objects.
        """
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def bounded_fetch(client, id, title):
            async with semaphore:
                try:
                    results = await self._fetch_scrap_async(id=id, title=title, client=client)
                    await asyncio.sleep(1)
                    return results
                
                except Exception as e:
                    print(f"Failed for '{title}': {e}")
                    return None

        async with httpx.AsyncClient() as client:
            tasks = [ bounded_fetch(client=client, id=pair[0], title=pair[1]) for pair in id_title_pairs ]
            results = await asyncio.gather(*tasks)

        return [ result for result in results if result is not None ]


    def fetch_plot(self, title):
        url = self._find_url(title)
        soup = self._get_soup(url)
        plot = self._get_plot(soup)
        return plot


#region Coonection
    def _find_url(self, title):
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": title,
            "format": "json"
        }
        response = self._parse_response(search_url, params=params)

        if not response:
            return None
        
        return self._build_url(response.json())
        

    def _get_soup(self, url):
        if not url:
            print("URL is not valid.")
            return None
        
        response = self._parse_response(url)

        if not response:
            print("No results.")
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        return soup


#region Async
    async def _fetch_scrap_async(self, id, title, client: httpx.AsyncClient):
        # url = await self._find_url_async(title, client)  # the search title wiki API limits the number of requests, difficult to call in chunk.
        url = self._build_url_str(title)

        if not url:
            return None
        
        soup = await self._get_soup_async(url, client)

        if not soup:
            return None
        
        name = self._get_title(soup)
        infobox = self._get_infobox(soup)
        plot = self._get_plot(soup)

        if not plot:
            return None
        
        scrap = {
            'id': id,
            'title': name,
            'infobox': infobox,
            'plot': plot
        }
        return WikiScrap.model_validate(scrap)

    async def _find_url_async(self, title, client: httpx.AsyncClient):
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": title,
            "format": "json"
        }
        response = await self._parse_response_async(client=client, url=search_url, params=params)
        
        if not response:
            return None
        
        return self._build_url(response.json())
        

    async def _get_soup_async(self, url, client: httpx.AsyncClient):
        if not url:
            print("URL is not valid.")
            return None
        
        response = await self._parse_response_async(client=client, url=url)

        if not response:
            print("No results.")
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        return soup


#region Data Handling
    def _build_url(self, json) -> str | None:
        hits = json['query']['search']

        if hits:
            best_match = json['query']['search'][0]['title']
            url = "https://en.wikipedia.org/wiki/" + best_match.replace(" ", "_")
            return url
        else:
            print("No match on Wikipedia")
            return None

    def _build_url_str(self, title):
        if not title:
            return None
        
        url = "https://en.wikipedia.org/wiki/" + title.replace(" ", "_")
        return url


    def _get_title(self, soup: BeautifulSoup):
        if not soup:
            return None
        
        h1 = soup.find("h1")
        return h1.text


    def _get_plot(self, soup: BeautifulSoup):
        if not soup:
            return None
        
        plot_head = soup.find(id="Plot")

        if plot_head:
            plot_div = plot_head.parent
            paragraphs = plot_div.find_next_siblings("p")
            plot_text = "\n\n".join(p.text for p in paragraphs)
            return plot_text
        else:
            return "No plot available"


    def _get_infobox(self, soup: BeautifulSoup):
        if not soup:
            return None
        
        infobox = soup.find("table", {"class": "infobox"})
        
        if not infobox:
            return None
        
        rows = infobox.find_all("tr")
        final = self._handle_infobox(rows)
        return final
    

    def _handle_infobox(self, rows):
        info = {}

        for row in rows:
            header = row.find("th")
            data = row.find("td")

            if header and data:
                items = data.find_all("li")

                if items:
                    value = ", ".join(li.text.strip() for li in items)
                else:
                    value = data.text.strip()

                info[header.text.strip()] = value

        info_clean = {
            key.replace("\xa0", " "): value.replace("\xa0", " ") for key, value in info.items()
        }
        return info_clean


#region Utility
    def _parse_response(self, url, params=None) -> requests.Response | None:
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response

        except requests.exceptions.Timeout:
            print("Timeout: Wikipedia took too long to respond")
            return None

        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e}")
            return None


    async def _parse_response_async(self, client: httpx.AsyncClient, url, params=None):
        try:
            response = await client.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response
        
        except httpx.TimeoutException:
            print("Timeout: Wikipedia took too long to respond")
            return None

        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e}")
            return None

        except httpx.RequestError as e:
            print(f"Request error: {e}")
            return None

#region Testing
if __name__ == "__main__":
    scraper = WikipediaScraper()
    # result = asyncio.run(scraper.fetch_scrap_list(
    #     titles=[
    #         "Carol",
    #         'Portrait of a lady on fire',
    #         'Her private hell'
    #     ],
    #     max_concurrent=20
    # ))
    # print(result)