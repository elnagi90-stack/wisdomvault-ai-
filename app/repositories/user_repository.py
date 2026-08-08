from __future__ import annotations

from typing import Protocol

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.user import User


class SupportsSession(Protocol):
    def __call__(self) -> Session: ...


class UserRepository:
    def __init__(self, session_factory: SupportsSession):
        self._session_factory = session_factory

    def create(self, user: User) -> User:
        with self._session_factory() as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def get_by_id(self, user_id: str) -> User | None:
        with self._session_factory() as session:
            return session.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        with self._session_factory() as session:
            stmt = select(User).where(User.email == email)
            return session.scalar(stmt)

    def get_by_username(self, username: str) -> User | None:
        with self._session_factory() as session:
            stmt = select(User).where(User.username == username)
            return session.scalar(stmt)

    def get_by_email_or_username(self, value: str) -> User | None:
        with self._session_factory() as session:
            stmt = select(User).where(
                or_(
                    User.email == value,
                    User.username == value,
                )
            )
            return session.scalar(stmt)

    def list_all(self) -> list[User]:
        with self._session_factory() as session:
            stmt = select(User).order_by(User.created_at.desc())
            return list(session.scalars(stmt).all())

    def update(self, user: User) -> User:
        with self._session_factory() as session:
            merged = session.merge(user)
            session.commit()
            session.refresh(merged)
            return merged

    def delete(self, user_id: str) -> bool:
        with self._session_factory() as session:
            user = session.get(User, user_id)

            if user is None:
                return False

            session.delete(user)
            session.commit()
            return True
