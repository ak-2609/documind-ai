import logging
from datetime import datetime, timezone
from dataclasses import dataclass
from uuid import UUID

from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.services.groq_service import GroqService, NO_ANSWER_MESSAGE
from app.services.retrieval_service import RetrievalService, RetrievedChunk

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ChatResult:
    conversation_id: UUID
    answer: str
    citations: list[dict[str, str | int]]


class ConversationNotFoundError(ValueError):
    pass


class ChatService:
    def __init__(self, db: Session, retrieval_service: RetrievalService, groq_service: GroqService) -> None:
        self.db = db
        self.retrieval_service = retrieval_service
        self.groq_service = groq_service

    def _get_or_create_conversation(self, user: User, question: str, conversation_id: UUID | None) -> Conversation:
        if conversation_id is not None:
            conversation = self.db.get(Conversation, conversation_id)
            if conversation is None or conversation.user_id != user.id:
                raise ConversationNotFoundError("Conversation was not found.")
            return conversation
        conversation = Conversation(user_id=user.id, title=question[:255])
        self.db.add(conversation)
        self.db.flush()
        return conversation

    @staticmethod
    def _citations(chunks: list[RetrievedChunk]) -> list[dict[str, str | int]]:
        seen: set[tuple[str, int]] = set()
        citations: list[dict[str, str | int]] = []
        for chunk in chunks:
            key = (chunk.document_name, chunk.page_number)
            if key not in seen:
                seen.add(key)
                citations.append({"document_name": chunk.document_name, "page_number": chunk.page_number})
        return citations

    async def answer(
        self, user: User, question: str, conversation_id: UUID | None = None
    ) -> ChatResult:
        conversation = self._get_or_create_conversation(user, question, conversation_id)
        self.db.add(Message(conversation_id=conversation.id, role="user", content=question))

        chunks = await run_in_threadpool(self.retrieval_service.retrieve, question, user.id)
        if not chunks:
            answer, citations = NO_ANSWER_MESSAGE, []
        else:
            answer = await run_in_threadpool(self.groq_service.generate_answer, question, chunks)
            citations = [] if answer == NO_ANSWER_MESSAGE else self._citations(chunks)

        self.db.add(Message(conversation_id=conversation.id, role="assistant", content=answer, citations=citations))
        conversation.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        logger.info("Stored chat response conversation_id=%s user_id=%s", conversation.id, user.id)
        return ChatResult(conversation_id=conversation.id, answer=answer, citations=citations)
