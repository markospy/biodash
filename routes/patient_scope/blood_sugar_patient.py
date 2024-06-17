from typing import Annotated

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from models.models import Patient
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


router = APIRouter(prefix="/patient/blood_sugar", tags=["Patient Blood sugar"])


@router.post("/")
def add(
    current_patient: Annotated[Patient, Security(get_current_user, scopes=["patient"])],
    measurement: BloodSugarLevel,
    db: Session = Depends(get_db),
):
    """**Adds a new measurement of the blood sugar level**"""
    return add_measurement(measurement, "by patient", model_db=bsl, db=db)


@router.get("/", response_model=BloodSugarLevelOutList)
def get(
    current_patient: Annotated[Patient, Security(get_current_user, scopes=["patient"])],
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


@router.put("/")
def update(
    current_patient: Annotated[Patient, Security(get_current_user, scopes=["patient"])],
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
    current_patient: Annotated[Patient, Security(get_current_user, scopes=["patient"])],
    db: Session = Depends(get_db),
):
    """**Deletes all measurement** for a patient"""
    return delete_measurements(model_db=bsl, db=db, patient_id=current_patient.id)


@router.delete("/{measurement_id}", summary="Delete measures by ID")
def delete(
    current_patient: Annotated[Patient, Security(get_current_user, scopes=["patient"])],
    measurement_id: int,
    db: Session = Depends(get_db),
):
    """**Deletes a measurement** by a id"""
    return delete_measurements(model_db=bsl, db=db, measurement_id=measurement_id)
