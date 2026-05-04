import requests
from bs4 import BeautifulSoup

TRENDING_URL = "https://github.com/trending"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def parse_stars(text: str) -> int:
    text = text.strip().replace(",", "").replace(" ", "")
    if not text:
        return 0
    try:
        return int(text)
    except ValueError:
        return 0


def fetch_trending() -> list[dict]:
    resp = requests.get(TRENDING_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    repos = []
    for article in soup.select("article.Box-row"):
        # name
        h2 = article.select_one("h2.h3 a")
        if not h2:
            continue
        href = h2["href"]                        # e.g. "/ruvnet/ruflo"
        name = href.lstrip("/")                   # "ruvnet/ruflo"
        url = "https://github.com" + href

        # description
        desc_el = article.select_one("p")
        description = desc_el.get_text(strip=True) if desc_el else ""

        # language
        lang_el = article.select_one("[itemprop='programmingLanguage']")
        language = lang_el.get_text(strip=True) if lang_el else ""

        # total stars
        star_links = article.select("a.Link--muted")
        total_stars = 0
        if len(star_links) >= 1:
            total_stars = parse_stars(star_links[0].get_text(strip=True))

        # stars today
        stars_today = 0
        today_el = article.select_one("span.d-inline-block.float-sm-right")
        if today_el:
            raw = today_el.get_text(strip=True)
            # e.g. "1,234 stars today"
            stars_today = parse_stars(raw.split()[0])

        repos.append({
            "name": name,
            "url": url,
            "description": description,
            "language": language,
            "stars_today": stars_today,
            "total_stars": total_stars,
        })

    return repos


if __name__ == "__main__":
    results = fetch_trending()
    print(f"抓到 {len(results)} 筆")
    for r in results[:5]:
        print(r)
