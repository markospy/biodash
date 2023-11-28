from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies.dependencies import get_db
from cruds.user import register
from schemas.schemas import UserSchema

router = APIRouter(prefix="register", tags=["Registration"])


@router.post()
def register_user(db: Session = Depends(get_db)):
    """User registration"""
    register(db, UserSchema)
