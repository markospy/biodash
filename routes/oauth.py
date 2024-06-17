from typing import Annotated
from datetime import datetime, timedelta, UTC

from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel, ValidationError
from jose.exceptions import JWTError

from dependencies.dependencies import get_db
from models.models import Doctor, Patient
from schemas.schemas import DoctorScopes, PatientScopes
from env_loader import EnvLoader

env_loader = EnvLoader()

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: str | None = None
    scopes: list[str] = []


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"])


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(id: str, db: Session):
    user = db.scalar(select(Doctor).where(Doctor.id == id))

    if user:
        return DoctorScopes(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            specialty=user.specialty,
            password=user.password,
            scopes=["doctor", "patient"],
        )
    else:
        user = db.scalar(select(Patient).where(Patient.id == id))
        if user:
            user = user.__dict__
            user["scopes"] = ["patient"]
            return PatientScopes(**user)


def authenticate_user(db: Session, identification: str, password: str):
    user = get_user(identification, db)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


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
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, env_loader.secrete_key, algorithms=env_loader.algorithm)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, user_id=user_id)
    except (JWTError, ValidationError):
        raise credentials_exception
    user = get_user(token_data.user_id, db)
    if not user:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Token:
    """**Wait by doctor ID and Password**"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=env_loader.acces_token_expire_minutes)

    scopes = [user.scopes[0]]
    if len(user.scopes) == 2:
        scopes = [user.scopes[0], user.scopes[1]]

    print("Scope: ", scopes)
    access_token = create_access_token(
        data={"sub": user.id, "scopes": scopes},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")
