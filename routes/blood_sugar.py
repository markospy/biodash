from typing import Annotated
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models.models import Doctor
from models.models import BloodSugarLevel as bsl
from dependencies.dependencies import get_db
from schemas.schemas import BloodSugarLevelOut as bsOut
from schemas.schemas import BloodSugarLevelIn as bsIn
from routes.jwt_oauth_doctor import get_current_user
from cruds.measures import (
    add_measurement,
    get_all_measurements,
    delete_all_measurements,
    update_measurement,
)


def manage_null_values(measurement: bsOut, result):
    if measurement.date == None:
        measurement.date = result.date
    if measurement.value == None:
        measurement.value = result.value
    return measurement.date, measurement.value


router = APIRouter(prefix="/blood_sugar", tags=["Blood sugar"])


@router.post("")
def add(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    measurement: bsIn,
    db: Session = Depends(get_db),
):
    """**Adds a new measurement of the blood sugar level**"""
    return add_measurement(measurement, current_doctor.id, model_db=bsl, db=db)


@router.get(
    "/{patient_id}",
    response_model=list[bsOut],
)
def get(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    patient_id: str,
    db: Session = Depends(get_db),
):
    """**Obtains all measurements of the patient's blood sugar level**"""
    measurements = get_all_measurements(patient_id, model_db=bsl, db=db)
    return [
        bsOut(date=measurement.date, value=measurement.value)
        for measurement in measurements
    ]


@router.put("/{patient_id}_{date}")
def update(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    patient_id: int,
    date: datetime,
    measurement: bsOut,
    db: Session = Depends(get_db),
):
    """**Update a measurement**"""
    return update_measurement(
        manage_null_values,
        patient_id,
        date,
        measurement,
        model_db=bsl,
        db=db,
    )


@router.delete("")
def delete(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    patient_id: str,
    date: datetime | None = None,
    db: Session = Depends(get_db),
):
    """**Deletes a measurement** for a patient on the specified date and time"""
    return delete_all_measurements(
        model_db=bsl, db=db, patient_id=patient_id, date=date
    )
