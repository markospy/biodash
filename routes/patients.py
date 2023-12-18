# from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session

from models.models import Patient
from dependencies.dependencies import get_db
from schemas.schemas import PatientSchema

# from routes.jwt_oauth_user import get_current_user


router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("/add")
def add_patient(patient: PatientSchema, db: Session = Depends(get_db)):
    db.add(Patient(**patient.model_dump()))
    db.commit()
    return JSONResponse(
        f"The patient {patient.first_name} {patient.last_name} has successfully added."
    )


@router.get("/patient", response_model=PatientSchema)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    stmt = select(Patient).where(Patient.id == patient_id)
    result = db.scalars(stmt).first()
    if not result:
        raise HTTPException(status_code=404, detail="There are no registered patients")
    return PatientSchema(
        first_name=result.first_name,
        second_name=result.second_name,
        last_name=result.last_name,
        age=result.age,
        gender=result.gender,
        height=result.height,
        weight=result.weight,
        username=result.username,
    )


@router.put("/modify")
def update_patient(
    patient_id: int, patient: PatientSchema, db: Session = Depends(get_db)
):
    stmt = select(Patient).where(Patient.id == patient_id)
    result = db.scalars(stmt).all()
    if not result:
        raise HTTPException(status_code=404, detail="There are no registered patients")
    stmt = (
        update(Patient).where(Patient.id == patient_id).values(**patient.model_dump())
    )
    db.execute(stmt)
    db.commit()
    return JSONResponse(
        f"The info of the patient {patient.first_name} {patient.last_name} has been changed successfully."
    )


@router.delete("/delete")
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
):
    stmt = select(Patient).where(Patient.id == patient_id)
    result = db.scalars(stmt).all()
    if not result:
        raise HTTPException(status_code=404, detail="There are no registered patients")
    stmt = delete(Patient).where(Patient.id == patient_id)
    db.execute(stmt)
    db.commit()
    return JSONResponse(f"The user patient {patient_id} has been successfully deleted.")
