from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Security
from fastapi.responses import JSONResponse
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from dependencies.dependencies import get_db
from models.models import CardiovascularParameter, Doctor, Patient
from schemas.schemas import AnalizeCardiovascular, Analize, WarningCardiovascularParameter
from routes.oauth import get_current_user
from routes.calc.calculation import make_analize
from models.exceptions import exception_if_not_exists


router = APIRouter(prefix="/analize", tags=["Analize"])


@router.get("/blood_pressure", response_model=AnalizeCardiovascular)
def analize(
    current_doctor: Annotated[Doctor, Security(get_current_user, scopes=["doctor"])],
    patient_id: str,
    db: Session = Depends(get_db),
):
    """**Get the mean, minimum and maximum value of blood pressure and heart rate**"""

    minimum_systolic, maximum_systolic, mean_systolic = make_analize(
        patient_id, db, CardiovascularParameter.systolic, CardiovascularParameter
    )
    minimum_diastolic, maximum_diastolic, mean_diastolic = make_analize(
        patient_id, db, CardiovascularParameter.diastolic, CardiovascularParameter
    )
    minimum_heart_rate, maximum_heart_rate, mean_heart_rate = make_analize(
        patient_id, db, CardiovascularParameter.heart_rate, CardiovascularParameter
    )

    return AnalizeCardiovascular(
        systolic=Analize(minimum=minimum_systolic, maximum=maximum_systolic, mean=mean_systolic),
        diastolic=Analize(minimum=minimum_diastolic, maximum=maximum_diastolic, mean=mean_diastolic),
        heart_rate=Analize(minimum=minimum_heart_rate, maximum=maximum_heart_rate, mean=mean_heart_rate),
    )


@router.get("/warning_cardiovascular_parameter", response_model=list[WarningCardiovascularParameter])
def get_warning_patients(
    current_doctor: Annotated[Doctor, Security(get_current_user, scopes=["doctor"])],
    systolic: int | None = 120,
    diastolic: int | None = 80,
    heart_rate: int | None = 100,
    day: int | None = 1,
    hours: int | None = 0,
    db: Session = Depends(get_db),
):
    stmt = select(CardiovascularParameter).where(
        CardiovascularParameter.date >= (datetime.now() - timedelta(days=day, hours=hours)),
        or_(
            CardiovascularParameter.systolic >= systolic,
            CardiovascularParameter.diastolic >= diastolic,
            CardiovascularParameter.heart_rate >= heart_rate,
        ),
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
        patient_dict["systolic"] = measures.systolic
        patient_dict["diastolic"] = measures.diastolic
        patient_dict["heart_rate"] = measures.heart_rate
        patient_dict["date"] = measures.date
        patient_dict["first_name"] = patient.first_name
        patient_dict["last_name"] = patient.last_name
        patient_list.append(WarningCardiovascularParameter(**patient_dict))

    return patient_list
