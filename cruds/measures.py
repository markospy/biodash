# CRUDs for vital parameters
from datetime import datetime

from fastapi.responses import JSONResponse
from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session

from models.exceptions import exception_if_not_exists, exception_if_already_exists


# Create
def add_measurement(measurement, doctor_id, model_db, db: Session):
    stmt = select(model_db).where(
        model_db.patient_id == measurement.patient_id,
        model_db.date == measurement.date,
    )
    result = db.execute(stmt).first()
    exception_if_already_exists(result, "Measurement already exists.")
    measurement_dict = measurement.model_dump()
    measurement_dict["doctor_id"] = doctor_id
    db.add(model_db(**measurement_dict))
    db.commit()
    return JSONResponse("The measurement was saved correctly")


# Read
def get_all_measurements(patient_id: str, model_db, db: Session):
    """**Obtains all measurements of the patient's cardiovascular parameters**"""
    stmt = select(model_db).where(model_db.patient_id == patient_id)
    results = db.scalars(stmt).all()
    exception_if_not_exists(results, detail=f"The patient with id {patient_id} has no records")
    return results


# Update
def update_measurement(func, measurment_id: int, measurement, model_db, db: Session):
    stmt = select(model_db).where(model_db.id == measurment_id)
    result = db.scalars(stmt).first()
    exception_if_not_exists(result, "There are no registered patients")
    func(measurement, result)

    stmt = update(model_db).where(model_db.id == measurment_id).values(**measurement.model_dump())
    db.execute(stmt)
    db.commit()
    return JSONResponse("The measurement has been changed successfully.")


# Delete
def delete_measurements(model_db, db: Session, patient_id: str | None = None, measurement_id: int | None = None):
    if patient_id:
        stmt = select(model_db).where(model_db.patient_id == patient_id)
        result = db.scalars(stmt).all()
        exception_if_not_exists(result, "This patient not have measurements")

        stmt = delete(model_db).where(model_db.patient_id == patient_id)
        db.execute(stmt)
        db.commit()
        return JSONResponse(f"All patient measurements with id {patient_id} have been successfully deleted.")
    else:
        stmt = select(model_db).where(model_db.id == measurement_id)
        result = db.scalars(stmt).one_or_none()
        exception_if_not_exists(result, "There is no such measurement")
        stmt = delete(model_db).where(model_db.id == measurement_id)
        db.execute(stmt)
        db.commit()
        return JSONResponse(f"Patient measurement with id {measurement_id} have been successfully deleted.")
