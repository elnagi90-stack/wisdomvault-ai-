from __future__ import annotations

from app.models.quote import Quote


def quote_to_notion_properties(quote: Quote) -> dict:
    """Maps a Quote row to Notion page properties.

    Assumes the target database has these properties:
    - "Quote" (title)
    - "Book" (rich_text)
    - "Chapter" (rich_text)
    - "Page" (number)
    - "Favorite" (checkbox)
    - "Language" (rich_text)
    """
    title_text = quote.text[:2000] if quote.text else ""

    properties: dict = {
        "Quote": {
            "title": [
                {"text": {"content": title_text}},
            ]
        },
        "Favorite": {"checkbox": bool(quote.is_favorite)},
        "Language": {
            "rich_text": [
                {"text": {"content": quote.language or ""}},
            ]
        },
    }

    if quote.book is not None:
        properties["Book"] = {
            "rich_text": [
                {"text": {"content": quote.book.title}},
            ]
        }

    if quote.chapter:
        properties["Chapter"] = {
            "rich_text": [
                {"text": {"content": quote.chapter}},
            ]
        }

    if quote.page_number is not None:
        properties["Page"] = {"number": quote.page_number}

    return properties
