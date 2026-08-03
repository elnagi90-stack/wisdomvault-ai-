from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeEntryCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1, max_length=1000)


class KnowledgeEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
