import json
import os
import time
from collections import deque
from urllib.parse import urljoin, urlparse, urldefrag

import requests
from bs4 import BeautifulSoup


START_URL = "https://www.sreedattha.ac.in/"
MAX_PAGES = 50
PRIORITY_URLS = [
    "https://www.sreedattha.ac.in/",
    "https://www.sreedattha.ac.in/sdes/academics/courses-offered-by-sdes",
    "https://www.sreedattha.ac.in/sdgi/academics/courses-offered-by-sdgi",
    "https://www.sreedattha.ac.in/sdes/academics/admission-criteria",
]

ALLOWED_DOMAINS = {
    "sreedattha.ac.in",
    "www.sreedattha.ac.in",
}

SKIP_EXTENSIONS = (
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".svg",
    ".webp",
    ".zip",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
)


def normalize_url(url):
    url = url.strip()
    url, _ = urldefrag(url)
    url = url.strip()
    return url.rstrip("/") or url


def is_allowed_url(url):
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        return False

    if parsed.netloc.lower() not in ALLOWED_DOMAINS:
        return False

    if parsed.path.lower().endswith(SKIP_EXTENSIONS):
        return False

    return True


def extract_page(url, session):
    response = session.get(
        url,
        timeout=20,
    )

    response.raise_for_status()

    content_type = response.headers.get(
        "Content-Type",
        "",
    )

    if "text/html" not in content_type.lower():
        return None

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    title = (
        soup.title.get_text(" ", strip=True)
        if soup.title
        else ""
    )

    # -----------------------------------------
    # Collect links before removing HTML
    # -----------------------------------------

    links = []

    for anchor in soup.find_all("a", href=True):
        absolute_url = urljoin(
            url,
            anchor["href"],
        )

        absolute_url = normalize_url(
            absolute_url
        )

        if is_allowed_url(absolute_url):
            links.append(absolute_url)

    links = list(dict.fromkeys(links))

    # -----------------------------------------
    # Remove obvious unwanted elements
    # -----------------------------------------

    for tag in soup.find_all(
        [
            "script",
            "style",
            "noscript",
            "svg",
            "iframe",
            "form",
        ]
    ):
        tag.decompose()

    # Remove footer when the website uses
    # a real HTML footer element
    for footer in soup.find_all("footer"):
        footer.decompose()

    # -----------------------------------------
    # Extract page text
    # -----------------------------------------

    body = soup.body

    if body is None:
        return None

    text = body.get_text(
        separator="\n",
        strip=True,
    )

    # -----------------------------------------
    # Clean empty and consecutive duplicate lines
    # -----------------------------------------

    lines = []
    previous_line = None

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        if line == previous_line:
            continue

        lines.append(line)
        previous_line = line

    cleaned_text = "\n".join(lines)

    return {
        "title": title,
        "url": url,
        "text": cleaned_text,
        "links": links,
    }


def crawl_website():
    session = requests.Session()

    session.headers.update(
        {
            "User-Agent": (
                "SreeDatthaChatbot/1.0 "
                "(educational website assistant)"
            )
        }
    )

    queue = deque(
    normalize_url(url)
    for url in PRIORITY_URLS
)

    visited = set()
    pages = []

    while queue and len(pages) < MAX_PAGES:
        url = queue.popleft()

        if url in visited:
            continue

        visited.add(url)

        print(
            f"[{len(pages) + 1}/{MAX_PAGES}] "
            f"Scraping: {url}"
        )

        try:
            page = extract_page(
                url,
                session,
            )

            if page is None:
                continue

            if len(page["text"]) < 100:
                print(
                    f"Skipped short page: {url}"
                )

                # Still follow links discovered
                # on the short page.
                for link in page["links"]:
                    if link not in visited:
                        queue.append(link)

                continue

            pages.append(
                {
                    "title": page["title"],
                    "url": page["url"],
                    "text": page["text"],
                }
            )

            for link in page["links"]:
                if link not in visited:
                    queue.append(link)

        except requests.RequestException as error:
            print(f"Skipped: {url}")
            print(f"Reason: {error}")

        time.sleep(0.3)

    return pages


def save_pages(pages):
    knowledge_folder = os.path.join(
        os.path.dirname(__file__),
        "knowledge",
    )

    os.makedirs(
        knowledge_folder,
        exist_ok=True,
    )

    output_file = os.path.join(
        knowledge_folder,
        "website_data.json",
    )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            pages,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print(f"Saved {len(pages)} pages.")
    print(f"File: {output_file}")


if __name__ == "__main__":
    scraped_pages = crawl_website()
    save_pages(scraped_pages)