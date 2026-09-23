import requests
from bs4 import BeautifulSoup


class WikipediaScraper:
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        }


#region Coonection
    def find_url(self, title):
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": title,
            "format": "json"
        }
        response = self._parse_response(search_url, params=params)
        return self.build_url(response.json())
        

    def get_soup(self, url):
        response = self._parse_response(url)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup


#region Data Handling
    def build_url(self, json) -> str:
        hits = json['query']['search']

        if hits:
            best_match = json['query']['search'][0]['title']
            url = "https://en.wikipedia.org/wiki/" + best_match.replace(" ", "_")
            return url
        else:
            print("No match on Wikipedia")
            return None


    def get_title(self, soup: BeautifulSoup):
        h1 = soup.find("h1")
        return h1.text


    def get_plot(self, soup: BeautifulSoup):
        plot_head = soup.find(id="Plot")

        if plot_head:
            plot_div = plot_head.parent
            paragraphs = plot_div.find_next_siblings("p")
            plot_text = "\n\n".join(p.text for p in paragraphs)
            return plot_text
        else:
            return "No plot available"


    def get_infobox(self, soup: BeautifulSoup):
        infobox = soup.find("table", {"class": "infobox"})
        rows = infobox.find_all("tr")
        final = self.handle_infobox(rows)
        return final
    

    def handle_infobox(self, rows):
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
    def _parse_response(self, url, params=None) -> requests.Response:
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response

        except requests.exceptions.Timeout:
            print("Timeout: TMDB took too long to respond")
            return None

        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e}")
            return None