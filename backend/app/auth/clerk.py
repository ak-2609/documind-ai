from dataclasses import dataclass
import logging
from typing import Any

import httpx
import jwt
from fastapi import HTTPException, status
from jwt import InvalidTokenError, PyJWKClient
from jwt.exceptions import PyJWKClientConnectionError, PyJWKClientError

from app.config import Settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class VerifiedClerkToken:
    subject: str
    claims: dict[str, Any]


@dataclass(frozen=True)
class ClerkUserProfile:
    clerk_user_id: str
    email: str | None
    first_name: str | None
    last_name: str | None
    image_url: str | None


class ClerkJWTVerifier:
    """Verifies Clerk session JWT signatures and standard registered claims."""

    def __init__(self, settings: Settings) -> None:
        self.issuer = settings.clerk_issuer.rstrip("/")
        self.audience = settings.clerk_jwt_audience or None
        self.jwk_client = PyJWKClient(settings.clerk_jwks_url, cache_keys=True, lifespan=3600)

    def verify(self, token: str) -> VerifiedClerkToken:
        header: dict[str, Any] = {}
        unverified_claims: dict[str, Any] = {}
        try:
            header = jwt.get_unverified_header(token)
            unverified_claims = jwt.decode(token, options={"verify_signature": False})
            logger.info(
                "Clerk JWT verification starting kid=%s alg=%s iss=%s sub=%s azp=%s aud=%s exp=%s expected_issuer=%s expected_audience=%s jwks_url=%s",
                header.get("kid"),
                header.get("alg"),
                unverified_claims.get("iss"),
                unverified_claims.get("sub"),
                unverified_claims.get("azp"),
                unverified_claims.get("aud"),
                unverified_claims.get("exp"),
                self.issuer,
                self.audience or "<disabled>",
                self.jwk_client.uri,
            )
            signing_key = self.jwk_client.get_signing_key_from_jwt(token)
            logger.info("Clerk JWKS signing key lookup succeeded kid=%s", signing_key.key_id)
            decode_options = {"verify_aud": self.audience is not None}
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                issuer=self.issuer,
                audience=self.audience,
                options=decode_options,
            )
        except PyJWKClientConnectionError as exc:
            logger.warning("Clerk JWKS connection failure type=%s message=%s", type(exc).__name__, str(exc))
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service is temporarily unavailable.",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc
        except (InvalidTokenError, PyJWKClientError) as exc:
            logger.warning(
                "Clerk JWT validation failed type=%s message=%s kid=%s iss=%s aud=%s expected_issuer=%s expected_audience=%s",
                type(exc).__name__, str(exc), header.get("kid"), unverified_claims.get("iss"),
                unverified_claims.get("aud"), self.issuer, self.audience or "<disabled>",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token.",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc
        except Exception as exc:
            logger.exception("Unexpected Clerk JWT verification failure type=%s", type(exc).__name__)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service is temporarily unavailable.",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        subject = claims.get("sub")
        if not isinstance(subject, str) or not subject:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token does not identify a user.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return VerifiedClerkToken(subject=subject, claims=claims)


class ClerkClient:
    """Small Clerk Backend API client used to synchronize authoritative user data."""

    def __init__(self, settings: Settings) -> None:
        self.base_url = settings.clerk_api_url.rstrip("/")
        self.secret_key = settings.clerk_secret_key

    async def get_user(self, clerk_user_id: str) -> ClerkUserProfile:
        headers = {"Authorization": f"Bearer {self.secret_key}"}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/users/{clerk_user_id}", headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == status.HTTP_404_NOT_FOUND:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Clerk user no longer exists.") from exc
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Unable to synchronize user details.") from exc
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Unable to synchronize user details.") from exc

        payload = response.json()
        primary_email_id = payload.get("primary_email_address_id")
        email = next(
            (item.get("email_address") for item in payload.get("email_addresses", []) if item.get("id") == primary_email_id),
            None,
        )
        return ClerkUserProfile(
            clerk_user_id=payload["id"],
            email=email,
            first_name=payload.get("first_name"),
            last_name=payload.get("last_name"),
            image_url=payload.get("image_url"),
        )
