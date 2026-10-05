from fastapi import Request
from fastapi.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from app.auth.clerk import ClerkJWTVerifier


class ClerkJWTMiddleware(BaseHTTPMiddleware):
    """Parse and verify bearer tokens before protected dependencies are evaluated."""

    def __init__(self, app, verifier: ClerkJWTVerifier) -> None:
        super().__init__(app)
        self.verifier = verifier

    async def dispatch(self, request: Request, call_next) -> Response:
        request.state.clerk_token = None
        authorization = request.headers.get("Authorization")
        if not authorization:
            return await call_next(request)

        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token.strip():
            return JSONResponse(status_code=401, content={"detail": "Invalid authorization header."}, headers={"WWW-Authenticate": "Bearer"})

        try:
            request.state.clerk_token = await run_in_threadpool(self.verifier.verify, token.strip())
        except Exception as exc:
            if hasattr(exc, "status_code") and hasattr(exc, "detail"):
                headers = getattr(exc, "headers", None) or {}
                return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}, headers=headers)
            raise
        return await call_next(request)
