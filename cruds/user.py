from fastapi import HTTPException, status
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from models.models import User
from schemas.schemas import UserIn, UserInDB
from routes.jwt_oauth_user import get_password_hash


def register(db: Session, user: UserIn):
    stmt = select(User).where(User.username == user.username)
    result = db.scalars(stmt).one_or_none()
    if result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="The user already exists."
        )

    # Encrypt the password entered by the user
    hashed_password = get_password_hash(user.password)
    user_bd = UserInDB(username=user.username, hashed_password=hashed_password)

    db.add(User(**user_bd.model_dump()))
    db.commit()


def change_password(db: Session, user: UserIn):
    """User change password"""
    stmt = select(User).where(User.username == user.username)
    result = db.scalars(stmt).one_or_none()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The user {user.username} does not exist.",
        )
    stmt = (
        update(User)
        .where(User.username == user.username)
        .values(hashed_password=get_password_hash(user.password))
    )
    db.execute(stmt)
    db.commit()


def del_user(db: Session, username: str):
    """Delete user"""
    stmt = select(User).where(User.username == username)
    result = db.scalars(stmt).one_or_none()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The user {username} does not exist.",
        )
    stmt = delete(User).where(User.username == username)
    db.execute(stmt)
    db.commit()
