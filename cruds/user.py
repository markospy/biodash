from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from models.models import User
from schemas.schemas import UserSchema

# instance of the  CryptContext  class
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str):
    """Function to hash the password"""
    return pwd_context.hash(password)


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


def login(db: Session, user: UserSchema):
    stmt = select(User).where(User.usename == UserSchema.username)
    result = db.scalars(stmt).one_or_none()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user does not exist",
        )
    if not pwd_context.verify(user.password, result.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return result
