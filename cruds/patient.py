from fastapi import status
from fastapi.exceptions import HTTPException

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.models import Patient
from schemas.schemas import PatientSchema


# Create
def add_patient(db: Session, patient: PatientSchema):
    stmt = select(Patient).where(Patient.patient_id == PatientSchema.patient_id)
    result = db.scalars(stmt).one_or_none()
    if result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="The patient already exists"
        )
    db.add(Patient(patient.model_dump()))


# Read
def get_patients(db: Session, name: str):
    stmt = select(Patient).where(
        Patient.first_name == name
    )  # .where(Patient.username == PatientSchema.username)
    result = db.scalars(stmt).all()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There are no registered patients",
        )
    return result
