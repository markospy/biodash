from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies.dependencies import get_db
from models.models import CardiovascularParameter, Doctor
from schemas.schemas import AnalizeCardiovascular, Analize
from routes.oauth import get_current_user
from routes.calc.calculation import make_analize


router = APIRouter(prefix="/analize", tags=["Analize"])


@router.get("/blood-pressure", response_model=AnalizeCardiovascular)
def analize(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    patient_id: str,
    db: Session = Depends(get_db),
):
    """**Get the mean, minimum and maximum value of blood pressure and heart rate**"""

    minimum_systolic, maximum_systolic, mean_systolic = make_analize(patient_id, db, CardiovascularParameter.systolic, CardiovascularParameter)
    minimum_diastolic, maximum_diastolic, mean_diastolic = make_analize(patient_id, db, CardiovascularParameter.diastolic, CardiovascularParameter)
    minimum_heart_rate, maximum_heart_rate, mean_heart_rate = make_analize(patient_id, db, CardiovascularParameter.heart_rate, CardiovascularParameter)



    return AnalizeCardiovascular(
        systolic=Analize(minimum=minimum_systolic, maximum=maximum_systolic, mean=mean_systolic),
        diastolic=Analize(minimum=minimum_diastolic, maximum=maximum_diastolic, mean=mean_diastolic),
        heart_rate=Analize(minimum=minimum_heart_rate, maximum=maximum_heart_rate, mean=mean_heart_rate)
        )