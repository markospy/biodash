from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Security
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from dependencies.dependencies import get_db
from models.models import BloodSugarLevel, Doctor, Patient
from schemas.schemas import Analize, WarningBloodSugar
from routes.oauth import get_current_user
from routes.calc.calculation import make_analize
from models.exceptions import exception_if_not_exists

router = APIRouter(prefix="/analize", tags=["Analize"])


@router.get("/blood_sugar", response_model=Analize)
def analize(
    current_doctor: Annotated[Doctor, Security(get_current_user, scopes=["doctor"])],
    patient_id: str,
    db: Session = Depends(get_db),
):
    """
    **Get the mean, minimum and maximum value of blood sugar**

    """
    minimum, maximum, mean = make_analize(patient_id, db, BloodSugarLevel.value, BloodSugarLevel)
    return Analize(minimum=minimum, maximum=maximum, mean=mean)


@router.get("/warning_blood_sugar", response_model=list[WarningBloodSugar])
def get_warning_patients(
    current_doctor: Annotated[Doctor, Security(get_current_user, scopes=["doctor"])],
    value: float | None = 6.1,
    day: int | None = 1,
    hours: int | None = 0,
    db: Session = Depends(get_db),
):
    stmt = select(BloodSugarLevel).where(
        BloodSugarLevel.value >= value,
        BloodSugarLevel.date >= (datetime.now() - timedelta(days=day, hours=hours)),
    )

    patients_measures = db.scalars(stmt).all()

    if not patients_measures:
        return JSONResponse("No hay pacientes con problemas", status_code=404)
    patient_dict = {}
    patient_list = []
    for measures in patients_measures:
        stmt = select(Patient).where(Patient.id == measures.patient_id)
        patient = db.scalars(stmt).first()
        exception_if_not_exists(patient, "Paciente no encontrado")

        patient_dict["patient_id"] = measures.patient_id
        patient_dict["value"] = measures.value
        patient_dict["date"] = measures.date
        patient_dict["first_name"] = patient.first_name
        patient_dict["last_name"] = patient.last_name
        patient_list.append(WarningBloodSugar(**patient_dict))

    return patient_list
