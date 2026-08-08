from __future__ import annotations

from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


class WebPageExtractor:
    """
    Fetch and extract readable text from a web page.

    This class deliberately does not try to identify quotes yet.
    Its only responsibility is:
        URL -> cleaned page text
    """

    def __init__(self) -> None:
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }

    def extract(
        self,
        url: str,
        max_chars: int = 100_000,
    ) -> str:
        url = url.strip()

        if not url:
            return ""

        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"}:
            return ""

        if not parsed.netloc:
            return ""

        if max_chars < 1:
            return ""

        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=15,
            )
            response.raise_for_status()
        except requests.RequestException:
            return ""

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        # Remove elements that normally contain navigation,
        # scripts, styling, advertisements, or page metadata.
        for element in soup.select(
            "script, style, noscript, svg, "
            "nav, header, footer, aside, "
            "form"
        ):
            element.decompose()

        # Prefer the main article/content area when available.
        content = (
            soup.select_one("article")
            or soup.select_one("main")
            or soup.select_one('[role="main"]')
            or soup.body
        )

        if content is None:
            return ""

        text = content.get_text(
            " ",
            strip=True,
        )

        # Normalize excessive whitespace.
        text = " ".join(text.split())

        if not text:
            return ""

        return text[:max_chars]
