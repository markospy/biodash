from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.models import User
from schemas.schemas import UserIn, UserInDB
from security.security import get_password_hash


# Register user
def register(db: Session, user: UserIn):
    stmt = select(User).where(User.usename == UserIn.username)
    result = db.scalars(stmt).one_or_none()
    if result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="The user already exists"
        )

    # Encrypt the password entered by the user
    hashed_password = get_password_hash(user.model_dump["password"])
    user_bd = UserInDB(
        username=user.model_dump()["username"], hashed_password=hashed_password
    )

    db.add(User(**user_bd.model_dump()))
