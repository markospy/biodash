from datetime import datetime, date

from pydantic import BaseModel

from models.models import Gender


class PatientOut(BaseModel):
    first_name: str
    second_name: str | None = None
    last_name: str | None = None
    age: int | None = None
    gender: Gender | None = None
    height: int | None = None
    weight: float | None = None


class PatientIn(PatientOut):
    password: str


class BloodPressureSchema(BaseModel):
    systolic: int
    diastolic: int
    heart_date: int | None = None
    date: date | None = None
    hour: datetime
    patient_id: int
