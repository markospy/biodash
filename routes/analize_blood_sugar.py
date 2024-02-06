from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from dependencies.dependencies import get_db
from models.models import BloodSugarLevel, Doctor
from schemas.schemas import AnalizeBloodSugar
from routes.jwt_oauth_doctor import get_current_user

router = APIRouter(prefix="/blood-sugar", tags=["Analize"])


@router.get("/mean", response_model=AnalizeBloodSugar)
def mean(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    patient_id: str,
    db: Session = Depends(get_db),
):
    """Get the average value of blood sugar"""
    stmt = select(func.avg(BloodSugarLevel.value)).where(
        BloodSugarLevel.patient_id == patient_id
    )
    result = db.scalar(stmt)
    if result == None:
        raise HTTPException(
            status_code=404,
            detail=f"The patient with id {patient_id} has no records",
        )
    return AnalizeBloodSugar(value=result)


@router.get("/minimum", response_model=AnalizeBloodSugar)
def minimum(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    patient_id: str,
    db: Session = Depends(get_db),
):
    """Get the minimum value of blood sugar"""
    stmt = select(func.min(BloodSugarLevel.value)).where(
        BloodSugarLevel.patient_id == patient_id
    )
    result = db.scalar(stmt)
    if result == None:
        raise HTTPException(
            status_code=404,
            detail=f"The patient with id {patient_id} has no records",
        )
    return AnalizeBloodSugar(value=result)


@router.get("/maximum", response_model=AnalizeBloodSugar)
def maximum(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    patient_id: str,
    db: Session = Depends(get_db),
):
    """Get the maximum value of blood sugar"""
    stmt = select(func.max(BloodSugarLevel.value)).where(
        BloodSugarLevel.patient_id == patient_id
    )
    result = db.scalar(stmt)
    if result == None:
        raise HTTPException(
            status_code=404,
            detail=f"The patient with id {patient_id} has no records",
        )
    return AnalizeBloodSugar(value=result)
