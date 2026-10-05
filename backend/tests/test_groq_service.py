import os
import unittest

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/documind")
os.environ.setdefault("CLERK_ISSUER", "https://test.clerk.accounts.dev")
os.environ.setdefault("CLERK_JWKS_URL", "https://test.clerk.accounts.dev/.well-known/jwks.json")
os.environ.setdefault("CLERK_SECRET_KEY", "sk_test")
os.environ.setdefault("GROQ_API_KEY", "test-key")

from app.services.groq_service import GroqService, GroqServiceError
from app.services.retrieval_service import RetrievedChunk


class FakeCompletions:
    def __init__(self, content: str | None) -> None:
        self.content = content
        self.call = None

    def create(self, **kwargs):
        self.call = kwargs
        message = type("Message", (), {"content": self.content})()
        return type("Completion", (), {"choices": [type("Choice", (), {"message": message})()]})()


class FakeClient:
    def __init__(self, content: str | None) -> None:
        self.chat = type("Chat", (), {"completions": FakeCompletions(content)})()


class GroqServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.chunks = [RetrievedChunk("doc-1", "Notes.pdf", 4, "Grounded source text.", 0.9)]

    def test_only_grounded_context_is_sent_to_groq(self) -> None:
        service = GroqService.__new__(GroqService)
        service.model = "openai/gpt-oss-20b"
        service.max_output_tokens = 1024
        service.client = FakeClient("Grounded answer")

        self.assertEqual(service.generate_answer("What is documented?", self.chunks), "Grounded answer")
        request = service.client.chat.completions.call
        self.assertEqual(request["model"], "openai/gpt-oss-20b")
        self.assertEqual(request["temperature"], 0.0)
        self.assertIn("Grounded source text.", request["messages"][1]["content"])
        self.assertEqual(len(request["messages"]), 2)

    def test_empty_groq_answer_fails_safely(self) -> None:
        service = GroqService.__new__(GroqService)
        service.model = "openai/gpt-oss-20b"
        service.max_output_tokens = 1024
        service.client = FakeClient(None)

        with self.assertRaisesRegex(GroqServiceError, "empty answer"):
            service.generate_answer("What is documented?", self.chunks)
