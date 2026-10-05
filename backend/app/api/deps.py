from collections.abc import Generator
from typing import Annotated

from chromadb.api import ClientAPI
from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.clerk import VerifiedClerkToken
from app.database.session import SessionLocal
from app.models.user import User
from app.services.user import UserService

# This declaration adds OpenAPI's HTTP bearer scheme. JWT verification remains
# exclusively in ClerkJWTMiddleware, before this dependency is evaluated.
clerk_bearer_scheme = HTTPBearer(
    scheme_name="ClerkBearerAuth",
    description="Paste a valid Clerk session JWT. The token is verified against Clerk's JWKS.",
    auto_error=False,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_chroma_client(request: Request) -> ClientAPI:
    return request.app.state.chroma_client


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    _: Annotated[HTTPAuthorizationCredentials | None, Security(clerk_bearer_scheme)] = None,
) -> User:
    """Require a verified Clerk session and synchronize its user record."""
    token: VerifiedClerkToken | None = getattr(request.state, "clerk_token", None)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    service = UserService(db=db, clerk_client=request.app.state.clerk_client)
    return await service.sync_from_clerk(token.subject)
