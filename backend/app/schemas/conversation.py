from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CitationResponse(BaseModel):
    document_name: str
    page_number: int


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: str
    content: str
    citations: list[CitationResponse] = Field(default_factory=list)
    created_at: datetime

    @field_validator("citations", mode="before")
    @classmethod
    def normalize_citations(cls, value: object) -> object:
        return [] if value is None else value


class ConversationListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationDetail(ConversationListItem):
    messages: list[MessageResponse]


class ConversationRenameRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
