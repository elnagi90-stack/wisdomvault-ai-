from __future__ import annotations

from app.models.tag import Tag
from app.repositories.tag_repository import (
    SupportsSession,
    TagRepository,
)
from app.schemas.tag import TagUpdate


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

        name = name.strip()

        if not name:
            raise ValueError("Tag name cannot be empty.")

        existing = self.repository.get_by_name(name)

        if existing:
            raise ValueError("Tag already exists.")

        tag = Tag(
            name=name,
            color=color,
        )

        return self.repository.create(tag)

    def list_tags(self) -> list[Tag]:
        return self.repository.list_all()

    def get_tag(self, tag_id: str) -> Tag | None:
        return self.repository.get_by_id(tag_id)

    def update_tag(
        self,
        tag_id: str,
        payload: TagUpdate,
    ) -> Tag | None:

        fields = payload.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )

        if "name" in fields:
            name = fields["name"].strip()

            if not name:
                raise ValueError("Tag name cannot be empty.")

            fields["name"] = name

        return self.repository.update(
            tag_id,
            **fields,
        )

    def delete_tag(self, tag_id: str) -> bool:
        return self.repository.delete(tag_id)

    def search_tags(
        self,
        keyword: str,
    ) -> list[Tag]:

        keyword = keyword.strip()

        if not keyword:
            return []

        return self.repository.search(keyword)