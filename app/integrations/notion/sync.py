from __future__ import annotations

from app.integrations.notion.client import NotionClient
from app.integrations.notion.mapper import quote_to_notion_properties
from app.models.quote import Quote
from app.models.user import User
from app.repositories.quote_repository import QuoteRepository


class NotionNotConnectedError(Exception):
    pass


class NotionSyncService:
    def __init__(self, repository: QuoteRepository) -> None:
        self.repository = repository

    def sync_quote(self, quote: Quote, user: User) -> Quote:
        if not user.notion_access_token:
            raise NotionNotConnectedError(
                "This user has not connected a Notion account yet."
            )

        if not user.notion_quotes_database_id:
            raise NotionNotConnectedError(
                "No Notion database is configured for quotes yet."
            )

        client = NotionClient(user.notion_access_token)
        properties = quote_to_notion_properties(quote)

        if quote.notion_page_id:
            client.update_page(quote.notion_page_id, properties)
            return quote

        page = client.create_page(
            user.notion_quotes_database_id,
            properties,
        )

        updated = self.repository.update(
            quote.id,
            notion_page_id=page["id"],
        )

        return updated or quote
