from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from dependencies.dependencies import get_db
from models.models import BloodPressure

from schemas.schemas import AnalizeBloodPressure

router = APIRouter(prefix="/analize", tags=["Analize"])


@router.get("/blood-pressure/mean", response_model=AnalizeBloodPressure)
def mean(
    patient_id: int,
    systolic: bool = True,
    diastolic: bool = True,
    heart_rate: bool = True,
    db: Session = Depends(get_db),
):
    """Get the average value of blood pressure and heart rate"""
    stmt = select(BloodPressure).where(BloodPressure.patient_id == patient_id)
    results = db.scalars(stmt).all()
    if not results:
        raise HTTPException(
            status_code=404, detail=f"The patient with id {patient_id} has no records"
        )
    systolic_mean = None
    diastolic_mean = None
    heart_rate_mean = None
    if systolic:
        systolic_list = [measurement.systolic for measurement in results]
        systolic_mean = round(sum(systolic_list) / len(systolic_list), 0)
    if diastolic:
        diastolic_list = [measurement.diastolic for measurement in results]
        diastolic_mean = round(sum(diastolic_list) / len(diastolic_list), 0)
    if heart_rate:
        heart_rate_list = [measurement.heart_rate for measurement in results]
        heart_rate_mean = round(sum(heart_rate_list) / len(heart_rate_list), 0)

    analize = AnalizeBloodPressure(
        systolic=systolic_mean,
        diastolic=diastolic_mean,
        heart_rate=heart_rate_mean,
    )

    return analize


@router.get("/blood-pressure/minimum", response_model=AnalizeBloodPressure)
def minimum(
    patient_id: int,
    systolic: bool = True,
    diastolic: bool = True,
    heart_rate: bool = True,
    db: Session = Depends(get_db),
):
    """Get the minimum value of blood pressure and heart rate"""
    stmt = select(BloodPressure).where(BloodPressure.patient_id == patient_id)
    results = db.scalars(stmt).all()
    if not results:
        raise HTTPException(
            status_code=404, detail=f"The patient with id {patient_id} has no records"
        )
    systolic_min = None
    diastolic_min = None
    heart_rate_min = None
    if systolic:
        systolic_min = min([measurement.systolic for measurement in results])
    if diastolic:
        diastolic_min = min([measurement.diastolic for measurement in results])
    if heart_rate:
        heart_rate_min = min([measurement.heart_rate for measurement in results])

    analize = AnalizeBloodPressure(
        systolic=systolic_min,
        diastolic=diastolic_min,
        heart_rate=heart_rate_min,
    )

    return analize


@router.get("/blood-pressure/maximum", response_model=AnalizeBloodPressure)
def maximum(
    patient_id: int,
    systolic: bool = True,
    diastolic: bool = True,
    heart_rate: bool = True,
    db: Session = Depends(get_db),
):
    """Get the maximum value of blood pressure and heart rate"""
    stmt = select(BloodPressure).where(BloodPressure.patient_id == patient_id)
    results = db.scalars(stmt).all()
    if not results:
        raise HTTPException(
            status_code=404, detail=f"The patient with id {patient_id} has no records"
        )
    systolic_max = None
    diastolic_max = None
    heart_rate_max = None
    if systolic:
        systolic_max = max([measurement.systolic for measurement in results])
    if diastolic:
        diastolic_max = max([measurement.diastolic for measurement in results])
    if heart_rate:
        heart_rate_max = max([measurement.heart_rate for measurement in results])

    analize = AnalizeBloodPressure(
        systolic=systolic_max,
        diastolic=diastolic_max,
        heart_rate=heart_rate_max,
    )

    return analize
