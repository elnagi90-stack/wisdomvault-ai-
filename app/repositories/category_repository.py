from __future__ import annotations

from typing import Protocol

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.category import Category


class SupportsSession(Protocol):
    def __call__(self) -> Session:
        ...


class CategoryRepository:
    def __init__(self, session_factory: SupportsSession):
        self._session_factory = session_factory

    def create(self, category: Category) -> Category:
        with self._session_factory() as session:
            session.add(category)
            session.commit()
            session.refresh(category)
            return category

    def get_by_id(self, category_id: str) -> Category | None:
        with self._session_factory() as session:
            return session.get(Category, category_id)

    def get_by_name(self, name: str) -> Category | None:
        with self._session_factory() as session:
            stmt = select(Category).where(Category.name == name)
            return session.scalar(stmt)

    def list_all(self) -> list[Category]:
        with self._session_factory() as session:
            stmt = select(Category).order_by(Category.name)
            return list(session.scalars(stmt).all())

    def update(
        self,
        category_id: str,
        **fields,
    ) -> Category | None:
        with self._session_factory() as session:
            category = session.get(Category, category_id)

            if category is None:
                return None

            for key, value in fields.items():
                setattr(category, key, value)

            session.commit()
            session.refresh(category)

            return category

    def delete(self, category_id: str) -> bool:
        with self._session_factory() as session:
            category = session.get(Category, category_id)

            if category is None:
                return False

            session.delete(category)
            session.commit()

            return True

    def search(
        self,
        keyword: str,
    ) -> list[Category]:
        with self._session_factory() as session:
            stmt = select(Category).where(
                or_(
                    Category.name.ilike(f"%{keyword}%"),
                    Category.description.ilike(f"%{keyword}%"),
                )
            )

            return list(session.scalars(stmt).all())
