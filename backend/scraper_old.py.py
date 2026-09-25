import json
import os
import time
from collections import deque
from urllib.parse import urljoin, urlparse, urldefrag

import requests
from bs4 import BeautifulSoup


START_URL = "https://www.sreedattha.ac.in/"
MAX_PAGES = 50

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
    url, _ = urldefrag(url)
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
    response = session.get(url, timeout=20)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "")

    if "text/html" not in content_type.lower():
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.title.get_text(" ", strip=True) if soup.title else ""

    # Remove content that is not useful for chatbot knowledge
    for tag in soup(
        ["script", "style", "noscript", "svg", "iframe"]
    ):
        tag.decompose()

    # Extract readable text
    text = soup.get_text(separator="\n", strip=True)

    # Remove empty lines
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    cleaned_text = "\n".join(lines)

    # Find links to other pages
    links = []

    for anchor in soup.find_all("a", href=True):
        absolute_url = urljoin(url, anchor["href"])
        absolute_url = normalize_url(absolute_url)

        if is_allowed_url(absolute_url):
            links.append(absolute_url)

    # Remove duplicate links
    links = list(dict.fromkeys(links))

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

    queue = deque([normalize_url(START_URL)])

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
            page = extract_page(url, session)

            if page is None:
                continue

            # Ignore pages containing almost no useful text
            if len(page["text"]) < 100:
                continue

            pages.append(
                {
                    "title": page["title"],
                    "url": page["url"],
                    "text": page["text"],
                }
            )

            # Add discovered links to our queue
            for link in page["links"]:

                if link not in visited:
                    queue.append(link)

        except requests.RequestException as error:

            print(f"Skipped: {url}")
            print(f"Reason: {error}")

        # Small delay so we don't hammer the website
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