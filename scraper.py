import time
import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
URL = "https://en.wikipedia.org/wiki/List_of_countries_by_inflation_rate"
HEADERS = {"User-Agent": "Mozilla/5.0 (student project; contact: gokhulrajvelu.2005@gmail.com)"}


def fetch_page(url=URL, retries=3, timeout=10):
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt} failed: {e}")
            time.sleep(2 ** attempt)
    logger.error("All fetch attempts failed")
    return None


def parse_table(html):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="wikitable")
    if table is None:
        raise ValueError("Table not found - site layout may have changed")

    trs = table.find_all("tr")
    headers = [th.get_text(strip=True) for th in trs[0].find_all(["th", "td"])]
    if not headers or headers[0] != "Country":
        raise ValueError(f"Unexpected headers: {headers[:3]} - layout may have changed")

    rows = []
    for tr in trs[1:]:
        cells = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
        if len(cells) == len(headers):
            rows.append(dict(zip(headers, cells)))
    return rows


if __name__ == "__main__":
    html = fetch_page()
    rows = parse_table(html)
    print("Rows parsed:", len(rows))
    print(rows[0])