from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict


class AuthorBase(BaseModel):
    name: str
    bio: str | None = None
    nationality: str | None = None
    birth_year: int | None = None
    death_year: int | None = None


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(BaseModel):
    name: str | None = None
    bio: str | None = None
    nationality: str | None = None
    birth_year: int | None = None
    death_year: int | None = None


class AuthorResponse(AuthorBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
