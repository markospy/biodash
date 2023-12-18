from datetime import datetime

from pydantic import BaseModel

from models.models import Gender, User


class UserSchema(BaseModel):
    username: str


class UserIn(UserSchema):
    password: str


class UserInDB(UserSchema):
    hashed_password: str


class PatientSchema(BaseModel):
    first_name: str
    second_name: str | None = None
    last_name: str | None = None
    age: int | None = None
    gender: Gender | None = None
    height: int | None = None
    weight: float | None = None
    username: str


class BloodPressureSchema(BaseModel):
    systolic: int
    diastolic: int
    heart_rate: int | None = None
    date: datetime
    patient_id: int


class AnalizeBloodPressure(BaseModel):
    systolic: float | None = None
    diastolic: float | None = None
    heart_rate: float | None = None
