from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from dependencies.dependencies import get_db
from models.models import User
from schemas.schemas import UserIn, UserInDB, UserSchema
from routes.jwt_oauth_user import get_password_hash

# from routes.jwt_oauth_user import get_current_user


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
        hashed_password=get_password_hash(user.password),
    )
    db.add(User(**user_bd.model_dump()))
    db.commit()
    return JSONResponse(f"The user {user.username} has successfully registered.")


@router.get("/all", response_model=list[UserSchema])
def get_users(db: Session = Depends(get_db)):
    results = db.scalars(select(User)).all()
    if not results:
        raise HTTPException(status_code=404, detail="There are no registered users yet")
    return [UserSchema(username=row.username) for row in results]


@router.put("/change_password")
def update_password(
    user: UserIn,
    db: Session = Depends(get_db),
):
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
    return JSONResponse(
        f"The password of the user {user.username} has been changed successfully."
    )


@router.delete("/delete_user")
def delete_user(
    username: str,
    db: Session = Depends(get_db),
):
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
    return JSONResponse(f"The user {username} has been successfully deleted.")


# current_user: Annotated[UserIn, Depends(get_current_user)]
