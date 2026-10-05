import re
from dataclasses import dataclass

from app.services.pdf_service import ExtractedPage


@dataclass(frozen=True)
class TextChunk:
    page_number: int
    chunk_index: int
    text: str


class ChunkingService:
    """Creates overlapping, page-bounded character chunks for citation-safe retrieval."""

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_pages(self, pages: list[ExtractedPage]) -> list[TextChunk]:
        chunks: list[TextChunk] = []
        for page in pages:
            text = re.sub(r"\s+", " ", page.text).strip()
            start, chunk_index = 0, 0
            while start < len(text):
                proposed_end = min(start + self.chunk_size, len(text))
                end = proposed_end
                if proposed_end < len(text):
                    boundary = text.rfind(" ", start + (self.chunk_size // 2), proposed_end)
                    if boundary > start:
                        end = boundary
                chunk_text = text[start:end].strip()
                if chunk_text:
                    chunks.append(TextChunk(page_number=page.page_number, chunk_index=chunk_index, text=chunk_text))
                    chunk_index += 1
                if end >= len(text):
                    break
                start = max(end - self.chunk_overlap, start + 1)
        return chunks
