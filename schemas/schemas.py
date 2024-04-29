from pydantic import BaseModel, EmailStr, validator

from datetime import datetime

from models.models import Gender, Scholing


class EmailSchema(BaseModel):
    email_address: EmailStr
    email_verify: bool = False
    code: int
    doctor_id: str


class AddressSchema(BaseModel):
    address_id: int
    address: dict


class Doctor(BaseModel):
    id: str
    first_name: str
    second_name: str | None = None
    last_name: str | None = None
    specialty: str | None = None
    email_address: str | None = None


class DoctorOut(Doctor):
    email_verify: bool
    photo: str | None = None


class DoctorIn(Doctor):
    password: str


class DoctorUp(DoctorIn):
    id: str | None = None
    first_name: str | None = None
    password: str | None = None

    @validator("*", pre=True, allow_reuse=True)
    def check_null_values(cls, value):
        if value == "null":
            return None
        return value


class DoctorPhoto(Doctor):
    portrait: str | None = None


class PatientSchema(BaseModel):
    id: str
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
    address: dict | None = None


class PatientUp(PatientSchema):
    id: str | None = None
    first_name: str | None = None

    @validator("*", pre=True, allow_reuse=True)
    def check_null_values(cls, value):
        if value == "null":
            return None
        return value


class DoctorPatient(BaseModel):
    doctor_id: str
    patient_id: str


class CardiovascularParameterOut(BaseModel):
    systolic: int | None = None
    diastolic: int | None = None
    heart_rate: int | None = None
    date: datetime | None = None


class CardiovascularParameter(CardiovascularParameterOut):
    systolic: int = 120
    diastolic: int = 80
    patient_id: str


class BloodSugarLevelOut(BaseModel):
    date: datetime | None = None
    value: float | None = None


class BloodSugarLevelIn(BloodSugarLevelOut):
    patient_id: str


class AnalizeCardiovascular(BaseModel):
    systolic: float | None = None
    diastolic: float | None = None
    heart_rate: float | None = None


class AnalizeBloodSugar(BaseModel):
    minimum: float
    maximum: float
    mean: float
