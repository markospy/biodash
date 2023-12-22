from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from dependencies.dependencies import get_db
from models.models import BloodPressure, User
from schemas.schemas import AnalizeBloodPressure
from routes.jwt_oauth_user import get_current_user

router = APIRouter(prefix="/analize", tags=["Analize"])

list_params = [
    BloodPressure.systolic,
    BloodPressure.diastolic,
    BloodPressure.heart_rate,
]


@router.get("/blood-pressure/mean", response_model=AnalizeBloodPressure)
def mean(
    current_user: Annotated[User, Depends(get_current_user)],
    patient_id: int,
    systolic: bool = True,
    diastolic: bool = True,
    heart_rate: bool = True,
    db: Session = Depends(get_db),
):
    """Get the average value of blood pressure and heart rate"""
    list_results = []
    for value in list_params:
        if value == BloodPressure.systolic and not systolic:
            list_results.append(None)
        elif value == BloodPressure.diastolic and not diastolic:
            list_results.append(None)
        elif value == BloodPressure.heart_rate and not heart_rate:
            list_results.append(None)
        else:
            stmt = select(func.avg(value)).where(BloodPressure.patient_id == patient_id)
            result = db.scalar(stmt)
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"The patient with id {patient_id} has no records",
                )
            list_results.append(result)

    systolic_mean, diastolic_mean, heart_rate_mean = list_results

    analize = AnalizeBloodPressure(
        systolic=systolic_mean,
        diastolic=diastolic_mean,
        heart_rate=heart_rate_mean,
    )

    return analize


@router.get("/blood-pressure/minimum", response_model=AnalizeBloodPressure)
def minimum(
    current_user: Annotated[User, Depends(get_current_user)],
    patient_id: int,
    systolic: bool = True,
    diastolic: bool = True,
    heart_rate: bool = True,
    db: Session = Depends(get_db),
):
    """Get the minimum value of blood pressure and heart rate"""
    list_results = []
    for value in list_params:
        if value == BloodPressure.systolic and not systolic:
            list_results.append(None)
        elif value == BloodPressure.diastolic and not diastolic:
            list_results.append(None)
        elif value == BloodPressure.heart_rate and not heart_rate:
            list_results.append(None)
        else:
            stmt = select(func.min(value)).where(BloodPressure.patient_id == patient_id)
            result = db.scalar(stmt)
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"The patient with id {patient_id} has no records",
                )
            list_results.append(result)

    systolic_min, diastolic_min, heart_rate_min = list_results

    analize = AnalizeBloodPressure(
        systolic=systolic_min,
        diastolic=diastolic_min,
        heart_rate=heart_rate_min,
    )

    return analize


@router.get("/blood-pressure/maximum", response_model=AnalizeBloodPressure)
def maximum(
    current_user: Annotated[User, Depends(get_current_user)],
    patient_id: int,
    systolic: bool = True,
    diastolic: bool = True,
    heart_rate: bool = True,
    db: Session = Depends(get_db),
):
    """Get the maximum value of blood pressure and heart rate"""
    list_results = []
    for value in list_params:
        if value == BloodPressure.systolic and not systolic:
            list_results.append(None)
        elif value == BloodPressure.diastolic and not diastolic:
            list_results.append(None)
        elif value == BloodPressure.heart_rate and not heart_rate:
            list_results.append(None)
        else:
            stmt = select(func.max(value)).where(BloodPressure.patient_id == patient_id)
            result = db.scalar(stmt)
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"The patient with id {patient_id} has no records",
                )
            list_results.append(result)

    systolic_max, diastolic_max, heart_rate_max = list_results

    analize = AnalizeBloodPressure(
        systolic=systolic_max,
        diastolic=diastolic_max,
        heart_rate=heart_rate_max,
    )

    return analize
