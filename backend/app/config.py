from functools import lru_cache
from pathlib import Path

from pydantic import Field, PostgresDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated application configuration loaded from the environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        enable_decoding=False,
    )
    app_name: str = "DocuMind AI API"
    environment: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"
    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    database_url: PostgresDsn
    chroma_persist_directory: Path = Path("./data/chroma")
    chroma_collection_name: str = "document_chunks"
    clerk_issuer: str
    clerk_jwks_url: str
    clerk_secret_key: str
    clerk_jwt_audience: str | None = None
    clerk_api_url: str = "https://api.clerk.com/v1"
    max_upload_size_bytes: int = 25 * 1024 * 1024
    chunk_size: int = 1000
    chunk_overlap: int = 200
    embedding_model_name: str = "BAAI/bge-small-en-v1.5"
    embedding_batch_size: int = 32
    retrieval_top_k: int = 5
    retrieval_similarity_threshold: float = 0.45
    groq_api_key: SecretStr
    groq_model: str = "openai/gpt-oss-20b"
    groq_max_output_tokens: int = 1024

    @field_validator("groq_api_key")
    @classmethod
    def validate_groq_api_key(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            raise ValueError("GROQ_API_KEY must be configured")
        return value

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip().rstrip("/") for origin in value.split(",") if origin.strip()]
        return [origin.rstrip("/") for origin in value]

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        value = value.lower().strip()
        if value not in {"development", "test", "staging", "production"}:
            raise ValueError("ENVIRONMENT must be development, test, staging, or production")
        return value

    @field_validator("chunk_overlap")
    @classmethod
    def validate_chunk_overlap(cls, value: int, info) -> int:
        chunk_size = info.data.get("chunk_size", 1000)
        if value < 0 or value >= chunk_size:
            raise ValueError("CHUNK_OVERLAP must be at least 0 and smaller than CHUNK_SIZE")
        return value

    @field_validator("retrieval_top_k")
    @classmethod
    def validate_retrieval_top_k(cls, value: int) -> int:
        if value < 1 or value > 20:
            raise ValueError("RETRIEVAL_TOP_K must be between 1 and 20")
        return value

    @field_validator("retrieval_similarity_threshold")
    @classmethod
    def validate_similarity_threshold(cls, value: float) -> float:
        if not 0 <= value <= 1:
            raise ValueError("RETRIEVAL_SIMILARITY_THRESHOLD must be between 0 and 1")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
