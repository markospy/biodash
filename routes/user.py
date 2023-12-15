from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Annotated

from dependencies.dependencies import get_db
from cruds.user import register, change_password, del_user
from schemas.schemas import UserIn
from routes.jwt_oauth_user import get_current_user


router = APIRouter(prefix="/user", tags=["Users"])


@router.post("/register")
def register_user(
    user: UserIn,
    db: Session = Depends(get_db),
):
    register(db, user)
    return JSONResponse(f"The user {user.username} has successfully registered.")


@router.put("/change_password")
def update_password(
    user: UserIn,
    current_user: Annotated[UserIn, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    change_password(db, user)
    return JSONResponse(
        f"The password of the user {user.username} has been changed successfully."
    )


@router.delete("/delete_user")
def delete_user(
    username: str,
    current_user: Annotated[UserIn, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    del_user(db, username)
    return JSONResponse(f"The user {username} has been successfully deleted.")
