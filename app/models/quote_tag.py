from sqlalchemy import Column, ForeignKey, Table

from app.database.base import Base

quote_tags = Table(
    "quote_tags",
    Base.metadata,
    Column(
        "quote_id",
        ForeignKey("quotes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
