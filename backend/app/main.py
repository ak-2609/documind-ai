from contextlib import asynccontextmanager
import logging

import chromadb
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.auth.clerk import ClerkClient, ClerkJWTVerifier
from app.auth.middleware import ClerkJWTMiddleware
from app.config import get_settings
from app.services.chromadb_service import ChromaDBService
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.pdf_service import PDFService
from app.services.groq_service import GroqService
from app.services.retrieval_service import RetrievalService

settings = get_settings()
logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.chroma_persist_directory.mkdir(parents=True, exist_ok=True)
    app.state.chroma_client = chromadb.PersistentClient(path=str(settings.chroma_persist_directory))
    app.state.clerk_client = ClerkClient(settings)
    app.state.pdf_service = PDFService(settings.max_upload_size_bytes)
    app.state.chunking_service = ChunkingService(settings.chunk_size, settings.chunk_overlap)
    app.state.embedding_service = EmbeddingService(settings.embedding_model_name, settings.embedding_batch_size)
    app.state.chromadb_service = ChromaDBService(app.state.chroma_client, settings.chroma_collection_name)
    app.state.retrieval_service = RetrievalService(
        chroma_client=app.state.chroma_client,
        collection_name=settings.chroma_collection_name,
        embedding_service=app.state.embedding_service,
        top_k=settings.retrieval_top_k,
        similarity_threshold=settings.retrieval_similarity_threshold,
    )
    app.state.groq_service = GroqService(settings)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", debug=settings.debug, lifespan=lifespan, openapi_url=f"{settings.api_v1_prefix}/openapi.json", docs_url="/docs", redoc_url="/redoc")
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_credentials=True, allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"], allow_headers=["Authorization", "Content-Type", "X-Request-ID"])
app.add_middleware(ClerkJWTMiddleware, verifier=ClerkJWTVerifier(settings))
app.include_router(api_router, prefix=settings.api_v1_prefix)
