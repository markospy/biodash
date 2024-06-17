from typing import Annotated

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from models.models import Doctor
from models.models import BloodSugarLevel as bsl
from dependencies.dependencies import get_db
from schemas.schemas import BloodSugarLevel, BloodSugarLevelUpdate, BloodSugarLevelOutList, BloodSugarLevelOut
from routes.oauth import get_current_user
from cruds.measures import (
    add_measurement,
    get_all_measurements,
    delete_measurements,
    update_measurement,
)


def manage_null_values(measurement: BloodSugarLevel, result):
    if measurement.date == None:
        measurement.date = result.date
    if measurement.value == None:
        measurement.value = result.value
    return measurement.date, measurement.value


router = APIRouter(prefix="/blood_sugar", tags=["Blood sugar"])


@router.post("")
def add(
    current_doctor: Annotated[Doctor, Security(get_current_user, scopes=["doctor"])],
    measurement: BloodSugarLevel,
    db: Session = Depends(get_db),
):
    """**Adds a new measurement of the blood sugar level**"""
    return add_measurement(measurement, current_doctor.id, model_db=bsl, db=db)


@router.get("/{patient_id}", response_model=BloodSugarLevelOutList)
def get(
    current_doctor: Annotated[Doctor, Security(get_current_user, scopes=["doctor"])],
    patient_id: str,
    db: Session = Depends(get_db),
):
    """**Obtains all measurements of the patient's blood sugar level**"""
    measurements = get_all_measurements(patient_id, model_db=bsl, db=db)

    return BloodSugarLevelOutList(
        patient_id=patient_id,
        measures=[
            BloodSugarLevelOut(date=measurement.date, value=measurement.value, doctor=measurement.doctor_id)
            for measurement in measurements
        ],
    )


@router.put("")
def update(
    current_doctor: Annotated[Doctor, Security(get_current_user, scopes=["doctor"])],
    measurment_id: int,
    measurement: BloodSugarLevelUpdate,
    db: Session = Depends(get_db),
):
    """**Update a measurement**"""
    return update_measurement(
        manage_null_values,
        measurment_id,
        measurement,
        model_db=bsl,
        db=db,
    )


@router.delete("/all", summary="Delete all patient measures")
def delete(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    patient_id: str,
    db: Session = Depends(get_db),
):
    """**Deletes all measurement** for a patient"""
    return delete_measurements(model_db=bsl, db=db, patient_id=patient_id)


@router.delete("/{measurement_id}", summary="Delete measures by ID")
def delete(
    current_doctor: Annotated[Doctor, Security(get_current_user, scopes=["doctor"])],
    measurement_id: int,
    db: Session = Depends(get_db),
):
    """**Deletes a measurement** by a id"""
    return delete_measurements(model_db=bsl, db=db, measurement_id=measurement_id)
