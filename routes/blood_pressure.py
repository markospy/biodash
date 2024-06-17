from typing import Annotated

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from models.models import Doctor
from models.models import CardiovascularParameter as cvpm
from dependencies.dependencies import get_db
from schemas.schemas import (
    CardiovascularParameter,
    CardiovascularParameterOutList,
    CardiovascularParameterUpdate,
    CardiovascularParameterOut,
)
from routes.oauth import get_current_user
from cruds.measures import (
    add_measurement,
    get_all_measurements,
    delete_measurements,
    update_measurement,
)


def manage_null_values(measurement: CardiovascularParameterOut, result):
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


@router.post("/")
def add(
    current_doctor: Annotated[Doctor, Security(get_current_user, scopes=["doctor"])],
    measurement: CardiovascularParameter,
    db: Session = Depends(get_db),
):
    """**Adds a new measurement of the main cardiovascular parameters**"""
    return add_measurement(measurement, current_doctor.id, model_db=cvpm, db=db)


@router.get("/{patient_id}", response_model=CardiovascularParameterOut)
def get(
    current_doctor: Annotated[Doctor, Security(get_current_user, scopes=["doctor"])],
    patient_id: str,
    db: Session = Depends(get_db),
):
    """**Obtains all measurements of the patient's cardiovascular parameters**"""
    measurements = get_all_measurements(patient_id, model_db=cvpm, db=db)
    return CardiovascularParameterOutList(
        patient_id=patient_id,
        measures=[
            CardiovascularParameterOut(
                systolic=measurement.systolic,
                diastolic=measurement.diastolic,
                heart_rate=measurement.heart_rate,
                date=measurement.date,
            )
            for measurement in measurements
        ],
    )


@router.put("/")
def update(
    current_doctor: Annotated[Doctor, Security(get_current_user, scopes=["doctor"])],
    measurement_id: int,
    measurement: CardiovascularParameterUpdate,
    db: Session = Depends(get_db),
):
    """**Update a measurement**"""
    return update_measurement(
        manage_null_values,
        measurement_id,
        measurement,
        model_db=cvpm,
        db=db,
    )


@router.delete("/all", summary="Delete all patient measures")
def delete(
    current_doctor: Annotated[Doctor, Security(get_current_user, scopes=["doctor"])],
    patient_id: str,
    db: Session = Depends(get_db),
):
    """**Deletes all measurement** for a patient"""
    return delete_measurements(model_db=cvpm, db=db, patient_id=patient_id)


@router.delete("/{measurement_id}", summary="Delete measures by ID")
def delete(
    current_doctor: Annotated[Doctor, Security(get_current_user, scopes=["doctor"])],
    measurement_id: int,
    db: Session = Depends(get_db),
):
    """**Deletes a measurement** by a id"""
    return delete_measurements(model_db=cvpm, db=db, measurement_id=measurement_id)
