from sqlalchemy.orm import Session

from app.auth.clerk import ClerkClient
from app.models.user import User
from app.repositories.user import UserRepository


class UserService:
    def __init__(self, db: Session, clerk_client: ClerkClient) -> None:
        self.repository = UserRepository(db)
        self.clerk_client = clerk_client

    async def sync_from_clerk(self, clerk_user_id: str) -> User:
        profile = await self.clerk_client.get_user(clerk_user_id)
        return self.repository.upsert_from_clerk(profile)
