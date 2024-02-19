# CRUDs for vital parameters
from datetime import datetime

from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select, delete, update, and_
from sqlalchemy.orm import Session


# Create
def add_measurement(
    measurement,
    doctor_id,
    model_db,
    db: Session,
):
    stmt = select(model_db).where(
        and_(
            model_db.patient_id == measurement.patient_id,
            model_db.date == measurement.date,
        )
    )
    result = db.execute(stmt).first()
    if result:
        raise HTTPException(
            status_code=409, detail="Measurement already exists."
        )
    measurement_dict = measurement.model_dump()
    measurement_dict["doctor_id"] = doctor_id
    db.add(model_db(**measurement_dict))
    db.commit()
    return JSONResponse("The measurement was saved correctly")


# Read
def get_all_measurements(
    patient_id: str,
    model_db,
    db: Session,
):
    """**Obtains all measurements of the patient's cardiovascular parameters**"""
    stmt = select(model_db).where(model_db.patient_id == patient_id)
    results = db.scalars(stmt).all()
    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"The patient with id {patient_id} has no records",
        )
    return results


# Update
def update_measurement(
    func, patient_id: int, date: datetime, measurement, model_db, db: Session
):
    stmt = select(model_db).where(
        and_(model_db.patient_id == patient_id, model_db.date == date)
    )
    result = db.scalars(stmt).first()
    if not result:
        raise HTTPException(
            status_code=404, detail="There are no registered patients"
        )

    func(measurement, result)

    stmt = (
        update(model_db)
        .where(and_(model_db.patient_id == patient_id, model_db.date == date))
        .values(**measurement.model_dump())
    )
    db.execute(stmt)
    db.commit()
    return JSONResponse("The measurement has been changed successfully.")


# Delete
def delete_all_measurements(
    model_db,
    db: Session,
    patient_id: str,
    date: datetime | None = None,
):
    if date:
        stmt = select(model_db).where(
            and_(model_db.patient_id == patient_id, model_db.date == date)
        )
        result = db.scalars(stmt).all()
        if not result:
            raise HTTPException(
                status_code=404, detail="There is no such measurement"
            )
        stmt = delete(model_db).where(
            and_(model_db.patient_id == patient_id, model_db.date == date)
        )
        db.execute(stmt)
        db.commit()
        return JSONResponse(
            f"Patient measurement with id {patient_id} have been successfully deleted."
        )
    else:
        stmt = select(model_db).where(model_db.patient_id == patient_id)
        result = db.scalars(stmt).all()
        if not result:
            raise HTTPException(
                status_code=404, detail="There is no such measurement"
            )
        stmt = delete(model_db).where(model_db.patient_id == patient_id)
        db.execute(stmt)
        db.commit()
        return JSONResponse(
            f"All patient measurements with id {patient_id} have been successfully deleted."
        )
