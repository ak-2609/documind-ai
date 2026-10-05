from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.clerk import ClerkUserProfile
from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_clerk_user_id(self, clerk_user_id: str) -> User | None:
        return self.db.scalar(select(User).where(User.clerk_user_id == clerk_user_id))

    def upsert_from_clerk(self, profile: ClerkUserProfile) -> User:
        user = self.get_by_clerk_user_id(profile.clerk_user_id)
        if user is None:
            user = User(clerk_user_id=profile.clerk_user_id)
            self.db.add(user)

        user.email = profile.email
        user.first_name = profile.first_name
        user.last_name = profile.last_name
        user.image_url = profile.image_url
        self.db.commit()
        self.db.refresh(user)
        return user
