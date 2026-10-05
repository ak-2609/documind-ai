import os
import unittest
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/documind")
os.environ.setdefault("CLERK_ISSUER", "https://test.clerk.accounts.dev")
os.environ.setdefault("CLERK_JWKS_URL", "https://test.clerk.accounts.dev/.well-known/jwks.json")
os.environ.setdefault("CLERK_SECRET_KEY", "sk_test")
os.environ.setdefault("GROQ_API_KEY", "test-key")

from app.models.user import User
from app.services.chat_service import ChatService
from app.services.groq_service import NO_ANSWER_MESSAGE
from app.services.retrieval_service import RetrievalService, RetrievedChunk


class FakeEmbeddingService:
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        self.texts = texts
        return [[0.1, 0.2, 0.3]]


class FakeCollection:
    def query(self, **kwargs):
        self.kwargs = kwargs
        return {
            "documents": [["grounded text", "weak text"]],
            "metadatas": [[
                {"document_id": "doc-1", "document_name": "Notes.pdf", "page_number": 4, "chunk_text": "grounded text"},
                {"document_id": "doc-2", "document_name": "Other.pdf", "page_number": 8, "chunk_text": "weak text"},
            ]],
            "distances": [[0.2, 0.8]],
        }


class FakeChromaClient:
    def __init__(self):
        self.collection = FakeCollection()

    def get_collection(self, name: str):
        return self.collection


class FakeDatabase:
    def __init__(self):
        self.items = []

    def add(self, item) -> None:
        self.items.append(item)

    def flush(self) -> None:
        if getattr(self.items[-1], "id", None) is None:
            self.items[-1].id = uuid4()

    def commit(self) -> None:
        pass

    def get(self, model, identifier):
        return None


class EmptyRetrievalService:
    def retrieve(self, question, user_id):
        return []


class FailingGroqService:
    def generate_answer(self, question, chunks):
        raise AssertionError("Groq must not run when retrieval returns no grounded chunks")


class Phase4ServiceTests(unittest.IsolatedAsyncioTestCase):
    def test_retrieval_is_user_scoped_and_thresholded(self) -> None:
        chroma = FakeChromaClient()
        embeddings = FakeEmbeddingService()
        service = RetrievalService(chroma, "document_chunks", embeddings, top_k=5, similarity_threshold=0.45)

        user_id = uuid4()
        result = service.retrieve("What is the topic?", user_id)

        self.assertEqual(embeddings.texts, ["query: What is the topic?"])
        self.assertEqual(chroma.collection.kwargs["where"], {"user_id": str(user_id)})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].document_name, "Notes.pdf")
        self.assertEqual(result[0].page_number, 4)

    async def test_no_retrieval_returns_fallback_without_llm(self) -> None:
        database = FakeDatabase()
        user = User(id=uuid4(), clerk_user_id="user_test")
        service = ChatService(database, EmptyRetrievalService(), FailingGroqService())

        result = await service.answer(user, "Unrelated question")

        self.assertEqual(result.answer, NO_ANSWER_MESSAGE)
        self.assertEqual(result.citations, [])
        self.assertEqual(len(database.items), 3)
