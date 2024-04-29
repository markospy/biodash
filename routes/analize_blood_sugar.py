from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from dependencies.dependencies import get_db
from models.models import BloodSugarLevel, Doctor
from schemas.schemas import AnalizeBloodSugar
from routes.jwt_oauth_doctor import get_current_user
from models.exceptions import exception_if_not_exists, OperationError
from models.enumerations import Operation

router = APIRouter(prefix="/blood-sugar", tags=["Analize"])

def select_operation(operation: Operation, value: float):
    match operation:
        case Operation.minimum :
            return func.min(value)
        case Operation.maximum:
            return func.max(value)
        case Operation.mean:
            return func.avg(value)
        case _:
            e = OperationError("Operación invalida. Debe ser de tipo enum.Enum: Operation")
            return e.msj_error


def operation(patient_id: str, db: Session, operation: Operation):
    """
    **Get the mean, minimum or maximum value of blood sugar**

    """
    selected_operation = select_operation(operation, BloodSugarLevel.value)
    stmt = select(selected_operation).where(BloodSugarLevel.patient_id == patient_id)
    result = db.scalar(stmt)
    detail_error = f"The patient with id {patient_id} has no records"
    exception_if_not_exists(result, detail_error)
    return result


@router.get("/analize", response_model=AnalizeBloodSugar)
def analize(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    patient_id: str,
    db: Session = Depends(get_db),
):
    """
    **Get the mean, minimum and maximum value of blood sugar**

    """
    minimum = operation(patient_id, db, Operation.minimum)
    maximum = operation(patient_id, db, Operation.maximum)
    mean = operation(patient_id, db, Operation.mean)
    return AnalizeBloodSugar(minimum=minimum, maximum=maximum, mean=mean)