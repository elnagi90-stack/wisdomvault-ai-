from __future__ import annotations

from app.models.author import Author
from app.repositories.author_repository import (
    AuthorRepository,
    SupportsSession,
)


class AuthorService:
    def __init__(
        self,
        repository: AuthorRepository | None = None,
        session_factory: SupportsSession | None = None,
    ) -> None:
        if repository is not None:
            self.repository = repository
        elif session_factory is not None:
            self.repository = AuthorRepository(session_factory=session_factory)
        else:
            raise TypeError("Either repository or session_factory must be provided")

    def create_author(
        self,
        *,
        name: str,
        bio: str | None = None,
        nationality: str | None = None,
        birth_year: int | None = None,
        death_year: int | None = None,
    ) -> Author:

        name = name.strip()

        if not name:
            raise ValueError("Author name cannot be empty.")

        author = Author(
            name=name,
            bio=bio,
            nationality=nationality,
            birth_year=birth_year,
            death_year=death_year,
        )

        return self.repository.create(author)

    def list_authors(self) -> list[Author]:
        return self.repository.list_all()

    def get_author(
        self,
        author_id: str,
    ) -> Author | None:
        return self.repository.get_by_id(author_id)

    def update_author(
        self,
        author_id: str,
        *,
        name: str | None = None,
        bio: str | None = None,
        nationality: str | None = None,
        birth_year: int | None = None,
        death_year: int | None = None,
    ) -> Author | None:

        author = self.repository.get_by_id(author_id)

        if author is None:
            return None

        if name is not None:
            name = name.strip()

            if not name:
                raise ValueError("Author name cannot be empty.")

            author.name = name

        if bio is not None:
            author.bio = bio

        if nationality is not None:
            author.nationality = nationality

        if birth_year is not None:
            author.birth_year = birth_year

        if death_year is not None:
            author.death_year = death_year

        return self.repository.update(author)

    def delete_author(
        self,
        author_id: str,
    ) -> bool:
        return self.repository.delete(author_id)

    def search_authors(
        self,
        keyword: str,
    ) -> list[Author]:
        return self.repository.search(keyword)