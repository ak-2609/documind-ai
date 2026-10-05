import logging
from uuid import UUID, uuid4

from chromadb.api import ClientAPI

from app.services.chunking_service import TextChunk

logger = logging.getLogger(__name__)


class ChromaIndexError(RuntimeError):
    pass


class ChromaDBService:
    def __init__(self, client: ClientAPI, collection_name: str) -> None:
        self.client = client
        self.collection_name = collection_name

    def _collection(self):
        return self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def index_document(
        self,
        user_id: UUID,
        document_id: UUID,
        document_name: str,
        chunks: list[TextChunk],
        embeddings: list[list[float]],
    ) -> int:
        if len(chunks) != len(embeddings):
            raise ChromaIndexError("Chunk and embedding counts do not match.")
        if not chunks:
            raise ChromaIndexError("No text chunks were generated for this document.")

        ids = [f"{document_id}:{chunk.page_number}:{chunk.chunk_index}:{uuid4().hex}" for chunk in chunks]
        metadatas = [
            {
                "user_id": str(user_id),
                "document_id": str(document_id),
                "document_name": document_name,
                "page_number": chunk.page_number,
                "chunk_text": chunk.text,
            }
            for chunk in chunks
        ]
        try:
            collection = self._collection()
            for start in range(0, len(chunks), 100):
                end = start + 100
                collection.add(
                    ids=ids[start:end],
                    documents=[chunk.text for chunk in chunks[start:end]],
                    metadatas=metadatas[start:end],
                    embeddings=embeddings[start:end],
                )
            logger.info("Indexed %s chunks for document_id=%s", len(chunks), document_id)
            return len(chunks)
        except Exception as exc:
            logger.exception("ChromaDB indexing failed for document_id=%s", document_id)
            raise ChromaIndexError("Document chunks could not be indexed.") from exc

    def delete_document(self, document_id: UUID) -> None:
        try:
            self._collection().delete(where={"document_id": str(document_id)})
        except Exception:
            logger.exception("Failed to clean ChromaDB chunks for document_id=%s", document_id)
