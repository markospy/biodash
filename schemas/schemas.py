from pydantic import BaseModel, EmailStr

from datetime import datetime

from models.models import Gender, Scholing


class EmailSchema(BaseModel):
    email_id: int
    email_address: EmailStr
    email_verify: bool = False
    doctor_id: str


class AdressSchema(BaseModel):
    adress_id: int
    adress: dict


class DoctorOut(BaseModel):
    doctor_id: str
    first_name: str
    second_name: str | None = None
    last_name: str | None = None
    specialty: str | None = None
    password: str
    portrait: bytes | None = None


class DoctorIn(BaseModel):
    password: str


class Patient(BaseModel):
    patient_id: str
    first_name: str
    second_name: str | None = None
    last_name: str | None = None
    birth_date: datetime | None = None
    gender: Gender | None = None
    height: int | None = None
    weight: float | None = None
    scholing: Scholing | None = None
    employee: bool | None = None
    married: bool | None = None
    adress_id: int


class CardiovascularParameter(BaseModel):
    date: datetime
    systolic: int = 120
    diastolic: int = 80
    heart_rate: int | None = None
    patient_id: str
    doctor_id: str


class BloodSugarLevel(BaseModel):
    date: datetime
    value: float
    patient_id: str
    doctor_id: str
