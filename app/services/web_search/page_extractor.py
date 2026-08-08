from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class WebPageContent:
    html: str
    text: str


class WebPageExtractor:
    """
    Fetch and extract readable content from a web page.

    Returns both:
        - original HTML
        - cleaned readable text
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

    def extract_content(
        self,
        url: str,
        max_chars: int = 100_000,
    ) -> WebPageContent | None:

        url = url.strip()

        if not url:
            return None

        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"}:
            return None

        if not parsed.netloc:
            return None

        if max_chars < 1:
            return None

        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=15,
            )
            response.raise_for_status()
        except requests.RequestException:
            return None

        html = response.text

        if not html:
            return None

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        for element in soup.select(
            "script, style, noscript, svg, "
            "nav, header, footer, aside, "
            "form"
        ):
            element.decompose()

        content = (
            soup.select_one("article")
            or soup.select_one("main")
            or soup.select_one('[role="main"]')
            or soup.body
        )

        if content is None:
            return None

        text = content.get_text(
            " ",
            strip=True,
        )

        text = " ".join(text.split())

        if not text:
            return None

        return WebPageContent(
            html=html,
            text=text[:max_chars],
        )

    def extract(
        self,
        url: str,
        max_chars: int = 100_000,
    ) -> str:

        content = self.extract_content(
            url,
            max_chars=max_chars,
        )

        if content is None:
            return ""

        return content.text
