from typing import Annotated
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models.models import Doctor
from models.models import CardiovascularParameter as cvpm
from dependencies.dependencies import get_db
from schemas.schemas import CardiovascularParameter as cvps
from schemas.schemas import CardiovascularParameterOut as cvpsOut
from routes.jwt_oauth_doctor import get_current_user
from cruds.measures import (
    add_measurement,
    get_all_measurements,
    delete_all_measurements,
    update_measurement,
)


def manage_null_values(measurement: cvpsOut, result):
    if measurement.systolic == None:
        measurement.systolic = result.systolic
    if measurement.diastolic == None:
        measurement.diastolic = result.diastolic
    if measurement.heart_rate == None:
        measurement.heart_rate = result.heart_rate
    if measurement.date == None:
        measurement.date = result.date
    return (
        measurement.systolic,
        measurement.diastolic,
        measurement.heart_rate,
        measurement.date,
    )


router = APIRouter(prefix="/blood_pressure", tags=["Blood pressure"])


@router.post("/add")
def add(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    measurement: cvps,
    db: Session = Depends(get_db),
):
    """**Adds a new measurement of the main cardiovascular parameters**"""
    add_measurement(measurement, model_db=cvpm, db=db)


@router.get(
    "/{patient_id}/all_measurements",
    response_model=list[cvpsOut],
)
def get(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    patient_id: str,
    db: Session = Depends(get_db),
):
    """**Obtains all measurements of the patient's cardiovascular parameters**"""
    measurements = get_all_measurements(patient_id, model_db=cvpm, db=db)
    return [
        cvpsOut(
            systolic=measurement.systolic,
            diastolic=measurement.diastolic,
            heart_rate=measurement.heart_rate,
            date=measurement.date,
        )
        for measurement in measurements
    ]


@router.put("/{patient_id}_{date}")
def update(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    patient_id: int,
    date: datetime,
    measurement: cvpsOut,
    db: Session = Depends(get_db),
):
    """**Update a measurement**"""
    update_measurement(
        manage_null_values,
        patient_id,
        date,
        measurement,
        model_db=cvpm,
        db=db,
    )


@router.delete("/delete")
def delete(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    patient_id: str,
    date: datetime | None = None,
    db: Session = Depends(get_db),
):
    """**Deletes a measurement** for a patient on the specified date and time"""
    delete_all_measurements(
        model_db=cvpm, db=db, patient_id=patient_id, date=date
    )
