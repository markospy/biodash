from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select, delete, update, and_
from sqlalchemy.orm import Session

from models.models import Patient, User
from dependencies.dependencies import get_db
from schemas.schemas import PatientSchema, PatientSchemaIn
from routes.jwt_oauth_user import get_current_user


router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("/add")
def add_patient(
    current_user: Annotated[User, Depends(get_current_user)],
    patient: PatientSchema,
    db: Session = Depends(get_db),
):
    patient = PatientSchemaIn(doctor=current_user.username, **patient.model_dump())
    db.add(Patient(**patient.model_dump()))
    db.commit()
    return JSONResponse(
        f"The patient {patient.first_name} {patient.last_name} has successfully added."
    )


@router.get("/patient")
def get_patient(
    current_user: Annotated[User, Depends(get_current_user)],
    patient_id: int | None = None,
    db: Session = Depends(get_db),
):
    no_patients = HTTPException(
        status_code=404, detail="There are no registered patients"
    )
    if patient_id:
        stmt = select(Patient).where(
            and_(Patient.id == patient_id, Patient.doctor == current_user.username)
        )
        result = db.scalars(stmt).first()
        if not result:
            raise no_patients
        else:
            return PatientSchema(
                id=result.id,
                first_name=result.first_name,
                second_name=result.second_name,
                last_name=result.last_name,
                age=result.age,
                gender=result.gender,
                height=result.height,
                weight=result.weight,
            )
    else:
        stmt = select(Patient).where(Patient.doctor == current_user.username)
        results = db.scalars(stmt).all()
        if not results:
            raise no_patients
        else:
            return [
                PatientSchema(
                    id=result.id,
                    first_name=result.first_name,
                    second_name=result.second_name,
                    last_name=result.last_name,
                    age=result.age,
                    gender=result.gender,
                    height=result.height,
                    weight=result.weight,
                )
                for result in results
            ]


@router.put("/modify")
def update_patient(
    current_user: Annotated[User, Depends(get_current_user)],
    patient_id: int,
    patient: PatientSchema,
    db: Session = Depends(get_db),
):
    stmt = select(Patient).where(
        and_(Patient.id == patient_id, Patient.doctor == current_user.username)
    )
    result = db.scalars(stmt).all()
    if not result:
        raise HTTPException(status_code=404, detail="There are no registered patients")
    stmt = (
        update(Patient)
        .where(and_(Patient.id == patient_id, Patient.doctor == current_user.username))
        .values(**patient.model_dump())
    )
    db.execute(stmt)
    db.commit()
    return JSONResponse(
        f"The info of the patient {patient.first_name} {patient.last_name} has been changed successfully."
    )


@router.delete("/delete")
def delete_patient(
    current_user: Annotated[User, Depends(get_current_user)],
    patient_id: int,
    db: Session = Depends(get_db),
):
    stmt = select(Patient).where(
        and_(Patient.id == patient_id, Patient.doctor == current_user.username)
    )
    result = db.scalars(stmt).all()
    if not result:
        raise HTTPException(status_code=404, detail="There are no registered patients")
    stmt = delete(Patient).where(
        and_(Patient.id == patient_id, Patient.doctor == current_user.username)
    )
    db.execute(stmt)
    db.commit()
    return JSONResponse(f"The user patient {patient_id} has been successfully deleted.")
