from __future__ import annotations

from dataclasses import dataclass

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class PageMetadata:
    title: str | None = None
    author: str | None = None
    book: str | None = None


class PageMetadataExtractor:
    """
    Extract basic metadata from an HTML page.

    This class does not perform web requests.
    It receives HTML and extracts metadata such as:
        - page title
        - author
        - book title
    """

    def extract(self, html: str) -> PageMetadata:
        html = html.strip()

        if not html:
            return PageMetadata()

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        title = self._extract_title(soup)
        author = self._extract_author(soup)
        book = self._extract_book(soup)

        return PageMetadata(
            title=title,
            author=author,
            book=book,
        )

    def _extract_title(
        self,
        soup: BeautifulSoup,
    ) -> str | None:

        # Prefer OpenGraph title because it is usually
        # more descriptive than the generic HTML title.
        og_title = soup.select_one(
            'meta[property="og:title"]'
        )

        if og_title:
            content = self._meta_content(og_title)

            if content:
                return content

        title_element = soup.find("title")

        if title_element:
            title = title_element.get_text(
                " ",
                strip=True,
            )

            if title:
                return title

        return None

    def _extract_author(
        self,
        soup: BeautifulSoup,
    ) -> str | None:

        selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            'meta[name="article:author"]',
        ]

        for selector in selectors:
            element = soup.select_one(selector)

            if not element:
                continue

            content = self._meta_content(element)

            if content:
                return content

        return None

    def _extract_book(
        self,
        soup: BeautifulSoup,
    ) -> str | None:

        selectors = [
            'meta[name="book"]',
            'meta[property="book"]',
            'meta[name="book:title"]',
            'meta[property="book:title"]',
        ]

        for selector in selectors:
            element = soup.select_one(selector)

            if not element:
                continue

            content = self._meta_content(element)

            if content:
                return content

        return None

    @staticmethod
    def _meta_content(element) -> str | None:
        content = element.get("content")

        if not content:
            return None

        content = str(content).strip()

        return content or None