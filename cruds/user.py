from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.models import User
from schemas.schemas import UserSchema


# Register user
def register(db: Session, user: UserSchema):
    stmt = select(User).where(User.usename == UserSchema.username)
    result = db.scalars(stmt).one_or_none()
    if result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="The user already exists"
        )
    user.password = get_password_hash(
        user.password
    )  # Encrypt the password entered by the user
    db.add(User(user.model_dump()))
