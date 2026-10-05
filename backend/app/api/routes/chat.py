from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService, ConversationNotFoundError
from app.services.groq_service import GroqServiceError
from app.services.retrieval_service import RetrievalServiceError

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, summary="Answer a question from the user's uploaded documents")
async def chat(
    payload: ChatRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatResponse:
    service = ChatService(
        db=db,
        retrieval_service=request.app.state.retrieval_service,
        groq_service=request.app.state.groq_service,
    )
    try:
        result = await service.answer(current_user, payload.question, payload.conversation_id)
    except ConversationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except GroqServiceError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except RetrievalServiceError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return ChatResponse(**result.__dict__)
