from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentListItem, DocumentUploadResponse
from app.services.document_indexing_service import DocumentIndexingError, DocumentIndexingService
from app.services.pdf_service import PDFExtractionError, PDFValidationError

router = APIRouter()


@router.get("/documents", response_model=list[DocumentListItem], summary="List the current user's documents")
def list_documents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[DocumentListItem]:
    return list(db.scalars(select(Document).where(Document.user_id == current_user.id).order_by(Document.created_at.desc())))


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a document and its indexed chunks")
def delete_document(document_id: UUID, request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Response:
    document = db.scalar(select(Document).where(Document.id == document_id, Document.user_id == current_user.id))
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document was not found.")
    request.app.state.chromadb_service.delete_document(document.id)
    db.delete(document)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED, summary="Upload and index a PDF")
async def upload_document(
    request: Request,
    file: UploadFile = File(..., description="PDF document to upload"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentUploadResponse:
    service = DocumentIndexingService(
        db=db,
        pdf_service=request.app.state.pdf_service,
        chunking_service=request.app.state.chunking_service,
        embedding_service=request.app.state.embedding_service,
        chromadb_service=request.app.state.chromadb_service,
    )
    try:
        document, chunk_count = await service.index_upload(file, current_user)
    except PDFValidationError as exc:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=str(exc)) from exc
    except PDFExtractionError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except DocumentIndexingError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    return DocumentUploadResponse(
        id=document.id,
        original_filename=document.original_filename,
        mime_type=document.mime_type,
        size_bytes=document.size_bytes,
        page_count=document.page_count or 0,
        processing_status=document.processing_status,
        chunks_indexed=chunk_count,
    )
