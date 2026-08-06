from __future__ import annotations

from app.models.tag import Tag
from app.repositories.tag_repository import (
    SupportsSession,
    TagRepository,
)


class TagService:
    def __init__(
        self,
        repository: TagRepository | None = None,
        session_factory: SupportsSession | None = None,
    ) -> None:
        if repository is not None:
            self.repository = repository
        elif session_factory is not None:
            self.repository = TagRepository(session_factory=session_factory)
        else:
            raise TypeError("Either repository or session_factory must be provided")

    def create_tag(
        self,
        *,
        name: str,
        color: str | None = None,
    ) -> Tag:

        if not name.strip():
            raise ValueError("Tag name cannot be empty.")

        tag = Tag(
            name=name.strip(),
            color=color,
        )

        return self.repository.create(tag)

    def list_tags(self) -> list[Tag]:
        return self.repository.list_all()

    def get_tag(self, tag_id: str) -> Tag | None:
        return self.repository.get_by_id(tag_id)

    def delete_tag(self, tag_id: str) -> bool:
        return self.repository.delete(tag_id)

    def search_tags(self, keyword: str) -> list[Tag]:
        return self.repository.search(keyword)
