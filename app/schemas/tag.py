from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict


class TagBase(BaseModel):
    name: str
    color: str | None = None


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: str | None = None
    color: str | None = None


class TagResponse(TagBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
