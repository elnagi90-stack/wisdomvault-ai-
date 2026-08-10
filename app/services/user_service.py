from __future__ import annotations

from app.models.user import User
from app.repositories.user_repository import (
    SupportsSession,
    UserRepository,
)
from app.core.security import (
    hash_password,
    verify_password,
)


class UserService:
    def __init__(
        self,
        repository: UserRepository | None = None,
        session_factory: SupportsSession | None = None,
    ) -> None:
        if repository is not None:
            self.repository = repository
        elif session_factory is not None:
            self.repository = UserRepository(session_factory=session_factory)
        else:
            raise TypeError(
                "Either repository or session_factory must be provided."
            )

    def register(
        self,
        *,
        username: str,
        email: str,
        password: str,
    ) -> User:

        username = username.strip()
        email = email.strip().lower()

        if not username:
            raise ValueError("Username cannot be empty.")

        if not email:
            raise ValueError("Email cannot be empty.")

        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters.")

        if self.repository.get_by_username(username):
            raise ValueError("Username already exists.")

        if self.repository.get_by_email(email):
            raise ValueError("Email already exists.")

        user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
        )

        return self.repository.create(user)

    def authenticate(
        self,
        *,
        email: str,
        password: str,
    ) -> User | None:

        user = self.repository.get_by_email(email.strip().lower())

        if user is None:
            return None

        if not verify_password(
            password,
            user.hashed_password,
        ):
            return None

        return user

    def get_user(
        self,
        user_id: str,
    ) -> User | None:
        return self.repository.get_by_id(user_id)

    def get_by_email(
        self,
        email: str,
    ) -> User | None:
        return self.repository.get_by_email(email)

    def list_users(
        self,
    ) -> list[User]:
        return self.repository.list_all()

    def delete_user(
        self,
        user_id: str,
    ) -> bool:
        return self.repository.delete(user_id)
