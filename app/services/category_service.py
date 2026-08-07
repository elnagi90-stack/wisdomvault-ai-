from __future__ import annotations

from app.models.category import Category
from app.repositories.category_repository import (
    CategoryRepository,
    SupportsSession,
)
from app.schemas.category import CategoryUpdate


class CategoryService:
    def __init__(
        self,
        repository: CategoryRepository | None = None,
        session_factory: SupportsSession | None = None,
    ) -> None:
        if repository is not None:
            self.repository = repository
        elif session_factory is not None:
            self.repository = CategoryRepository(session_factory=session_factory)
        else:
            raise TypeError("Either repository or session_factory must be provided")

    def create_category(
        self,
        *,
        name: str,
        description: str | None = None,
    ) -> Category:

        name = name.strip()

        if not name:
            raise ValueError("Category name cannot be empty.")

        existing = self.repository.get_by_name(name)

        if existing:
            raise ValueError("Category already exists.")

        category = Category(
            name=name,
            description=description,
        )

        return self.repository.create(category)

    def list_categories(self) -> list[Category]:
        return self.repository.list_all()

    def get_category(self, category_id: str) -> Category | None:
        return self.repository.get_by_id(category_id)

    def update_category(
        self,
        category_id: str,
        payload: CategoryUpdate,
    ) -> Category | None:

        fields = payload.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )

        if "name" in fields:
            name = fields["name"].strip()

            if not name:
                raise ValueError("Category name cannot be empty.")

            fields["name"] = name

        return self.repository.update(
            category_id,
            **fields,
        )

    def delete_category(self, category_id: str) -> bool:
        return self.repository.delete(category_id)

    def search_categories(
        self,
        keyword: str,
    ) -> list[Category]:

        keyword = keyword.strip()

        if not keyword:
            return []

        return self.repository.search(keyword)
