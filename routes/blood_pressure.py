from typing import Annotated
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select, delete, update, and_
from sqlalchemy.orm import Session

from models.models import BloodPressure, User
from dependencies.dependencies import get_db
from schemas.schemas import BloodPressureSchema
from routes.jwt_oauth_doctor import get_current_user

router = APIRouter(prefix="/blood_pressure", tags=["Blood pressure"])


@router.post("/add")
def add_measurement(
    current_user: Annotated[User, Depends(get_current_user)],
    measurement: BloodPressureSchema,
    db: Session = Depends(get_db),
):
    stmt = select(BloodPressure).where(
        and_(
            BloodPressure.patient_id == measurement.patient_id,
            BloodPressure.date == measurement.date,
        )
    )
    result = db.execute(stmt).first()
    if result:
        raise HTTPException(status_code=409, detail="Measurement already exists.")
    db.add(BloodPressure(**measurement.model_dump()))
    db.commit()
    return JSONResponse("The measurement was saved correctly")


@router.get("/{patient_id}/all_measurements", response_model=list[BloodPressureSchema])
def get_all_measurements(
    current_user: Annotated[User, Depends(get_current_user)],
    patient_id: int,
    db: Session = Depends(get_db),
):
    stmt = select(BloodPressure).where(BloodPressure.patient_id == patient_id)
    results = db.scalars(stmt).all()
    if not results:
        raise HTTPException(status_code=404, detail=f"The patient with id {patient_id} has no records")
    return [
        BloodPressureSchema(
            systolic=measurement.systolic,
            diastolic=measurement.diastolic,
            heart_rate=measurement.heart_rate,
            date=measurement.date,
            patient_id=measurement.patient_id,
        )
        for measurement in results
    ]


@router.put("/{patient_id}_{date}")
def update_measurement(
    current_user: Annotated[User, Depends(get_current_user)],
    patient_id: int,
    date: datetime,
    measurement: BloodPressureSchema,
    db: Session = Depends(get_db),
):
    stmt = select(BloodPressure).where(and_(BloodPressure.patient_id == patient_id, BloodPressure.date == date))
    result = db.scalars(stmt).all()
    if not result:
        raise HTTPException(status_code=404, detail="There are no registered patients")
    stmt = (
        update(BloodPressure)
        .where(and_(BloodPressure.patient_id == patient_id, BloodPressure.date == date))
        .values(**measurement.model_dump())
    )
    db.execute(stmt)
    db.commit()
    return JSONResponse("The measurement has been changed successfully.")


@router.delete("/delete")
def delete_all_measurements(
    current_user: Annotated[User, Depends(get_current_user)],
    patient_id: int,
    date: datetime | None = None,
    db: Session = Depends(get_db),
):
    if date:
        stmt = select(BloodPressure).where(BloodPressure.id == patient_id)
        result = db.scalars(stmt).all()
        if not result:
            raise HTTPException(status_code=404, detail="There are no registered patients")
        stmt = delete(BloodPressure).where(BloodPressure.patient_id == patient_id)
    else:
        stmt = select(BloodPressure).where(and_(BloodPressure.id == patient_id, BloodPressure.date == date))
        result = db.scalars(stmt).all()
        if not result:
            raise HTTPException(status_code=404, detail="There are no registered patients")
        stmt = delete(BloodPressure).where(and_(BloodPressure.id == patient_id, BloodPressure.date == date))
    db.execute(stmt)
    db.commit()
    return JSONResponse(f"Patient measurements with id {patient_id} have been successfully deleted.")
