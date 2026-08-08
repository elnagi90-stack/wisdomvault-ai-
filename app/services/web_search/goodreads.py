from __future__ import annotations

from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

from app.schemas.web_search.quote import WebQuoteResult
from app.services.web_search.cleaner import clean_quote_text


class GoodreadsQuoteScraper:
    def __init__(self) -> None:
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[WebQuoteResult]:

        query = query.strip()

        if not query or limit < 1:
            return []

        url = (
            "https://www.goodreads.com/quotes/search?q="
            + quote_plus(query)
        )

        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=15,
            )
            response.raise_for_status()
        except requests.RequestException:
            return []

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        results: list[WebQuoteResult] = []
        seen: set[str] = set()

        for item in soup.select("div.quoteText"):

            if len(results) >= limit:
                break

            # -----------------------------------------
            # Extract author before modifying the node
            # -----------------------------------------
            author = None

            author_element = item.select_one(
                "span.authorOrTitle"
            )

            if author_element:
                author = author_element.get_text(
                    " ",
                    strip=True,
                )

                if author:
                    author = author.rstrip(",")

            # -----------------------------------------
            # Extract book
            # -----------------------------------------
            book = None

            book_link = item.select_one(
                "a.bookTitle"
            )

            if book_link:
                book = book_link.get_text(
                    " ",
                    strip=True,
                )

            # -----------------------------------------
            # Work on a copy of the quote node
            # -----------------------------------------
            quote_node = BeautifulSoup(
                str(item),
                "html.parser",
            )

            # Remove author/book metadata.
            for element in quote_node.select(
                "span.authorOrTitle, "
                "a.authorOrTitle, "
                "a.bookTitle"
            ):
                element.decompose()

            raw_text = quote_node.get_text(
                " ",
                strip=True,
            )

            text = clean_quote_text(raw_text)

            if not text:
                continue

            # -----------------------------------------
            # Deduplicate
            # -----------------------------------------
            normalized = " ".join(
                text.lower().split()
            )

            if normalized in seen:
                continue

            seen.add(normalized)

            results.append(
                WebQuoteResult(
                    text=text,
                    author=author,
                    book=book,
                    source="Goodreads",
                    url=url,
                    score=None,
                )
            )

        return results
