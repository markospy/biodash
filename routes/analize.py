from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from dependencies.dependencies import get_db
from models.models import CardiovascularParameter, Doctor
from schemas.schemas import AnalizeCardiovascular
from routes.jwt_oauth_doctor import get_current_user

router = APIRouter(prefix="/analize", tags=["Analize"])

list_params = [
    CardiovascularParameter.systolic,
    CardiovascularParameter.diastolic,
    CardiovascularParameter.heart_rate,
]


@router.get("/blood-pressure/mean", response_model=AnalizeCardiovascular)
def mean(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    patient_id: int,
    systolic: bool = True,
    diastolic: bool = True,
    heart_rate: bool = True,
    db: Session = Depends(get_db),
):
    """Get the average value of blood pressure and heart rate"""
    list_results = []
    for value in list_params:
        if value == CardiovascularParameter.systolic and not systolic:
            list_results.append(None)
        elif value == CardiovascularParameter.diastolic and not diastolic:
            list_results.append(None)
        elif value == CardiovascularParameter.heart_rate and not heart_rate:
            list_results.append(None)
        else:
            stmt = select(func.avg(value)).where(
                CardiovascularParameter.patient_id == patient_id
            )
            result = db.scalar(stmt)
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"The patient with id {patient_id} has no records",
                )
            list_results.append(result)

    systolic_mean, diastolic_mean, heart_rate_mean = list_results

    analize = AnalizeCardiovascular(
        systolic=systolic_mean,
        diastolic=diastolic_mean,
        heart_rate=heart_rate_mean,
    )
    return analize


@router.get("/blood-pressure/minimum", response_model=AnalizeCardiovascular)
def minimum(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    patient_id: int,
    systolic: bool = True,
    diastolic: bool = True,
    heart_rate: bool = True,
    db: Session = Depends(get_db),
):
    """Get the minimum value of blood pressure and heart rate"""
    list_results = []
    for value in list_params:
        if value == CardiovascularParameter.systolic and not systolic:
            list_results.append(None)
        elif value == CardiovascularParameter.diastolic and not diastolic:
            list_results.append(None)
        elif value == CardiovascularParameter.heart_rate and not heart_rate:
            list_results.append(None)
        else:
            stmt = select(func.min(value)).where(
                CardiovascularParameter.patient_id == patient_id
            )
            result = db.scalar(stmt)
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"The patient with id {patient_id} has no records",
                )
            list_results.append(result)

    systolic_min, diastolic_min, heart_rate_min = list_results

    analize = AnalizeCardiovascular(
        systolic=systolic_min,
        diastolic=diastolic_min,
        heart_rate=heart_rate_min,
    )

    return analize


@router.get("/blood-pressure/maximum", response_model=AnalizeCardiovascular)
def maximum(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    patient_id: int,
    systolic: bool = True,
    diastolic: bool = True,
    heart_rate: bool = True,
    db: Session = Depends(get_db),
):
    """Get the maximum value of blood pressure and heart rate"""
    list_results = []
    for value in list_params:
        if value == CardiovascularParameter.systolic and not systolic:
            list_results.append(None)
        elif value == CardiovascularParameter.diastolic and not diastolic:
            list_results.append(None)
        elif value == CardiovascularParameter.heart_rate and not heart_rate:
            list_results.append(None)
        else:
            stmt = select(func.max(value)).where(
                CardiovascularParameter.patient_id == patient_id
            )
            result = db.scalar(stmt)
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"The patient with id {patient_id} has no records",
                )
            list_results.append(result)

    systolic_max, diastolic_max, heart_rate_max = list_results

    analize = AnalizeCardiovascular(
        systolic=systolic_max,
        diastolic=diastolic_max,
        heart_rate=heart_rate_max,
    )

    return analize
