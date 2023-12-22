from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from dependencies.dependencies import get_db
from models.models import User
from schemas.schemas import UserIn, UserInDB, UserSchema
from routes.jwt_oauth_user import get_password_hash, get_current_user


router = APIRouter(prefix="/user", tags=["Users"])


@router.post("/register")
def register_user(
    user: UserIn,
    db: Session = Depends(get_db),
):
    stmt = select(User).where(User.username == user.username)
    result = db.scalars(stmt).one_or_none()
    if result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="The user already exists."
        )
    user_bd = UserInDB(
        username=user.username,
        first_name=user.first_name,
        second_name=user.second_name,
        last_name=user.last_name,
        email=user.email,
        job=user.job,
        hashed_password=get_password_hash(user.password),
    )
    db.add(User(**user_bd.model_dump()))
    db.commit()
    return JSONResponse(f"The user {user.username} has successfully registered.")


@router.get("/me", response_model=UserSchema)
def get_users(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    result = db.scalars(
        select(User).where(User.username == current_user.username)
    ).one()
    if not result:
        raise HTTPException(status_code=404, detail="There are no registered users yet")
    return UserSchema(
        username=result.username,
        first_name=result.first_name,
        second_name=result.second_name,
        last_name=result.last_name,
        email=result.email,
        job=result.job,
    )


@router.put("/update_user")
def update_user(
    current_user: Annotated[User, Depends(get_current_user)],
    user: UserIn,
    db: Session = Depends(get_db),
):
    """User change password"""
    stmt = select(User).where(User.username == user.username)
    result = db.scalars(stmt).one()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The user {user.username} does not exist.",
        )
    if not user.first_name:
        first_name = result.first_name
    else:
        first_name = user.first_name
    if not user.second_name:
        second_name = result.second_name
    else:
        second_name = user.second_name
    if not user.last_name:
        last_name = result.last_name
    else:
        last_name = user.last_name
    if not user.email:
        email = result.email
    else:
        email = user.email
    if not user.job:
        job = result.job
    else:
        job = user.job
    if not user.password:
        password = result.hashed_password
    else:
        password = get_password_hash(user.password)
    stmt = (
        update(User)
        .where(User.username == current_user.username)
        .values(
            first_name=first_name,
            second_name=second_name,
            last_name=last_name,
            email=email,
            job=job,
            hashed_password=password,
        )
    )
    db.execute(stmt)
    db.commit()
    return JSONResponse(f"The {user.username}'s information was updated correctly.")


@router.delete("/delete_user")
def delete_user(
    current_user: Annotated[User, Depends(get_current_user)],
    username: str,
    db: Session = Depends(get_db),
):
    """Delete user"""
    if current_user.username != username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"You are not authorized to perform this action on the user {username}",
        )
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
    return JSONResponse(f"The user {username} has been successfully deleted.")
