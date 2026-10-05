from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.conversation import Conversation
from app.models.user import User


class ConversationNotFoundError(ValueError):
    pass


class ConversationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_user(self, user: User, offset: int = 0, limit: int | None = None) -> list[Conversation]:
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user.id)
            .order_by(Conversation.updated_at.desc())
        )
        if limit is not None:
            statement = statement.offset(offset).limit(limit)
        return list(self.db.scalars(statement))

    def get_for_user(self, user: User, conversation_id: UUID) -> Conversation:
        statement = (
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.id == conversation_id, Conversation.user_id == user.id)
        )
        conversation = self.db.scalar(statement)
        if conversation is None:
            raise ConversationNotFoundError("Conversation was not found.")
        return conversation

    def rename_for_user(self, user: User, conversation_id: UUID, title: str) -> Conversation:
        conversation = self.get_for_user(user, conversation_id)
        conversation.title = title.strip()
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def delete_for_user(self, user: User, conversation_id: UUID) -> None:
        conversation = self.get_for_user(user, conversation_id)
        self.db.delete(conversation)
        self.db.commit()
