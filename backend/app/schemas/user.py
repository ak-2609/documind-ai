from app.schemas.common import TimestampedSchema


class UserResponse(TimestampedSchema):
    clerk_user_id: str
    email: str | None
    first_name: str | None
    last_name: str | None
    image_url: str | None
