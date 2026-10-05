from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    conversation_id: UUID | None = None

    @field_validator("question")
    @classmethod
    def normalize_question(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("question must not be blank")
        return value


class CitationResponse(BaseModel):
    document_name: str
    page_number: int


class ChatResponse(BaseModel):
    conversation_id: UUID
    answer: str
    citations: list[CitationResponse]
