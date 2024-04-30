from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies.dependencies import get_db
from models.models import BloodSugarLevel, Doctor
from schemas.schemas import Analize
from routes.jwt_oauth_doctor import get_current_user
from routes.calc.calculation import make_analize

router = APIRouter(prefix="/analize", tags=["Analize"])


@router.get("/blood-sugar", response_model=Analize)
def analize(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    patient_id: str,
    db: Session = Depends(get_db),
):
    """
    **Get the mean, minimum and maximum value of blood sugar**

    """
    minimum, maximum, mean = make_analize(patient_id, db, BloodSugarLevel.value, BloodSugarLevel)
    return Analize(minimum=minimum, maximum=maximum, mean=mean)