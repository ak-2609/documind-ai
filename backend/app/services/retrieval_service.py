import logging
from dataclasses import dataclass
from uuid import UUID

from chromadb.api import ClientAPI

from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class RetrievalServiceError(RuntimeError):
    pass


@dataclass(frozen=True)
class RetrievedChunk:
    document_id: str
    document_name: str
    page_number: int
    text: str
    similarity: float


class RetrievalService:
    """Per-user semantic retrieval over the existing Chroma document collection."""

    def __init__(
        self,
        chroma_client: ClientAPI,
        collection_name: str,
        embedding_service: EmbeddingService,
        top_k: int,
        similarity_threshold: float,
    ) -> None:
        self.chroma_client = chroma_client
        self.collection_name = collection_name
        self.embedding_service = embedding_service
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold

    def retrieve(self, question: str, user_id: UUID) -> list[RetrievedChunk]:
        """Return only chunks at or above the configured cosine-similarity threshold."""
        query_embedding = self.embedding_service.embed_documents([f"query: {question}"])[0]
        try:
            collection = self.chroma_client.get_collection(self.collection_name)
            result = collection.query(
                query_embeddings=[query_embedding],
                n_results=self.top_k,
                where={"user_id": str(user_id)},
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            # A user who has never uploaded a document has no collection yet.
            if "does not exist" in str(exc).lower() or "not found" in str(exc).lower():
                return []
            logger.exception("ChromaDB retrieval failed for user_id=%s", user_id)
            raise RetrievalServiceError("Document retrieval is temporarily unavailable.") from exc

        documents = (result.get("documents") or [[]])[0] or []
        metadatas = (result.get("metadatas") or [[]])[0] or []
        distances = (result.get("distances") or [[]])[0] or []
        chunks: list[RetrievedChunk] = []
        for text, metadata, distance in zip(documents, metadatas, distances, strict=True):
            if not isinstance(metadata, dict):
                continue
            try:
                similarity = max(0.0, min(1.0, 1.0 - float(distance)))
                if similarity < self.similarity_threshold:
                    continue
                chunks.append(
                    RetrievedChunk(
                        document_id=str(metadata["document_id"]),
                        document_name=str(metadata["document_name"]),
                        page_number=int(metadata["page_number"]),
                        text=str(metadata.get("chunk_text") or text),
                        similarity=similarity,
                    )
                )
            except (KeyError, TypeError, ValueError):
                logger.warning("Skipped malformed ChromaDB metadata for user_id=%s", user_id)
        logger.info("Retrieved %s grounded chunks for user_id=%s", len(chunks), user_id)
        return chunks
