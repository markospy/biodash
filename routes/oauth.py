from typing import Annotated
from datetime import datetime, timedelta, UTC

from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel

from dependencies.dependencies import get_db
from models.models import Doctor
from schemas.schemas import DoctorIn
from env_loader import EnvLoader

env_loader = EnvLoader()

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    doctor_id: str | None = None


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"])


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(doctor_id: str, db: Session):
    doctor = db.scalars(
        select(Doctor).where(Doctor.id == doctor_id)
    ).one_or_none()
    if doctor:
        return DoctorIn(
            id=doctor.id,
            first_name=doctor.first_name,
            second_name=doctor.second_name,
            last_name=doctor.last_name,
            specialty=doctor.specialty,
            password=doctor.password,
            portrait=doctor.portrait,
        )


def authenticate_user(db: Session, identification: str, password: str):
    doctor = get_user(identification, db)
    if not doctor:
        return False
    if not verify_password(password, doctor.password):
        return False
    return doctor


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, env_loader.secrete_key, algorithm=env_loader.algorithm)
    return encoded_jwt


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, env_loader.secrete_key, algorithms=env_loader.algorithm)
        doctor: str = payload.get("sub")
        if doctor is None:
            raise credentials_exception
        token_data = TokenData(doctor_id=doctor)
    except JWTError:
        raise credentials_exception
    user = get_user(token_data.doctor_id, db)
    if not user:
        raise credentials_exception
    return user


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    """**Wait by doctor ID and Password**"""
    doctor = authenticate_user(db, form_data.username, form_data.password)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect doctor's id or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=env_loader.acces_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": doctor.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
