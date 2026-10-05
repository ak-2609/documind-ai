import logging
from dataclasses import dataclass
from io import BytesIO

import pdfplumber
from fastapi import UploadFile

logger = logging.getLogger(__name__)


class PDFValidationError(ValueError):
    pass


class PDFExtractionError(RuntimeError):
    pass


@dataclass(frozen=True)
class ExtractedPage:
    page_number: int
    text: str


class PDFService:
    def __init__(self, max_upload_size_bytes: int) -> None:
        self.max_upload_size_bytes = max_upload_size_bytes

    async def read_and_validate(self, upload: UploadFile) -> tuple[bytes, str, str]:
        try:
            filename = upload.filename or "document.pdf"
            if not filename.lower().endswith(".pdf"):
                raise PDFValidationError("Only PDF files are supported.")
            if upload.content_type not in {None, "application/pdf", "application/x-pdf"}:
                raise PDFValidationError("The uploaded file must have a PDF content type.")

            content = await upload.read(self.max_upload_size_bytes + 1)
            if not content:
                raise PDFValidationError("The uploaded PDF is empty.")
            if len(content) > self.max_upload_size_bytes:
                raise PDFValidationError(f"PDF files must not exceed {self.max_upload_size_bytes} bytes.")
            if not content.startswith(b"%PDF-"):
                raise PDFValidationError("The uploaded file is not a valid PDF.")
            return content, filename, "application/pdf"
        finally:
            await upload.close()

    def extract_pages(self, pdf_bytes: bytes) -> list[ExtractedPage]:
        try:
            with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
                pages = [
                    ExtractedPage(page_number=index, text=(page.extract_text() or "").strip())
                    for index, page in enumerate(pdf.pages, start=1)
                ]
        except Exception as exc:
            logger.warning("PDF extraction failed", exc_info=True)
            raise PDFExtractionError("The PDF could not be read.") from exc

        if not pages:
            raise PDFExtractionError("The PDF does not contain any pages.")
        if not any(page.text for page in pages):
            raise PDFExtractionError("The PDF does not contain extractable text.")
        return pages
