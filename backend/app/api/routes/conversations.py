from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.conversation import ConversationDetail, ConversationListItem, ConversationRenameRequest
from app.services.conversation_service import ConversationNotFoundError, ConversationService

router = APIRouter(prefix="/conversations")


@router.get("", response_model=list[ConversationListItem], summary="List the current user's conversations")
def list_conversations(offset: int = Query(0, ge=0), limit: int | None = Query(None, ge=1, le=100), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[ConversationListItem]:
    return ConversationService(db).list_for_user(current_user, offset, limit)


@router.get("/{conversation_id}", response_model=ConversationDetail, summary="Load a conversation and its messages")
def get_conversation(conversation_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ConversationDetail:
    try:
        return ConversationService(db).get_for_user(current_user, conversation_id)
    except ConversationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{conversation_id}", response_model=ConversationListItem, summary="Rename a conversation")
def rename_conversation(conversation_id: UUID, payload: ConversationRenameRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ConversationListItem:
    try:
        return ConversationService(db).rename_for_user(current_user, conversation_id, payload.title)
    except ConversationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a conversation and its messages")
def delete_conversation(conversation_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Response:
    try:
        ConversationService(db).delete_for_user(current_user, conversation_id)
    except ConversationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
