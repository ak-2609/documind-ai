import logging
from uuid import UUID, uuid4

from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.user import User
from app.services.chromadb_service import ChromaDBService
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.pdf_service import PDFExtractionError, PDFService

logger = logging.getLogger(__name__)


class DocumentIndexingError(RuntimeError):
    pass


class DocumentIndexingService:
    def __init__(
        self,
        db: Session,
        pdf_service: PDFService,
        chunking_service: ChunkingService,
        embedding_service: EmbeddingService,
        chromadb_service: ChromaDBService,
    ) -> None:
        self.db = db
        self.pdf_service = pdf_service
        self.chunking_service = chunking_service
        self.embedding_service = embedding_service
        self.chromadb_service = chromadb_service

    async def index_upload(self, upload: UploadFile, user: User) -> tuple[Document, int]:
        pdf_bytes, filename, mime_type = await self.pdf_service.read_and_validate(upload)
        document = Document(
            user_id=user.id,
            original_filename=filename,
            storage_key=f"uploads/{user.id}/{uuid4()}.pdf",
            mime_type=mime_type,
            size_bytes=len(pdf_bytes),
            processing_status="processing",
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)

        try:
            pages = await run_in_threadpool(self.pdf_service.extract_pages, pdf_bytes)
            chunks = await run_in_threadpool(self.chunking_service.chunk_pages, pages)
            if not chunks:
                raise DocumentIndexingError("No indexable text was found in the PDF.")
            embeddings = await run_in_threadpool(
                self.embedding_service.embed_documents, [chunk.text for chunk in chunks]
            )
            chunk_count = await run_in_threadpool(
                self.chromadb_service.index_document,
                user.id,
                document.id,
                document.original_filename,
                chunks,
                embeddings,
            )
            document.page_count = len(pages)
            document.processing_status = "indexed"
            document.processing_error = None
            self.db.commit()
            self.db.refresh(document)
            logger.info("Document indexed document_id=%s user_id=%s", document.id, user.id)
            return document, chunk_count
        except Exception as exc:
            self.chromadb_service.delete_document(document.id)
            document.processing_status = "failed"
            document.processing_error = str(exc)[:4000]
            self.db.commit()
            logger.exception("Document processing failed document_id=%s", document.id)
            if isinstance(exc, (DocumentIndexingError, PDFExtractionError)):
                raise
            raise DocumentIndexingError("The document could not be indexed.") from exc
