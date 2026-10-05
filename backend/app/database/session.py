from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings

settings = get_settings()
engine = create_engine(str(settings.database_url), pool_pre_ping=True, pool_size=5, max_overflow=10, pool_recycle=1800, echo=settings.debug)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
