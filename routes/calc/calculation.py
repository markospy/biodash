from sqlalchemy.orm import Session
from sqlalchemy import select, func


from models.exceptions import exception_if_not_exists, OperationError
from models.enumerations import Operation


def select_operation(operation: Operation, value: float):
    match operation:
        case Operation.minimum:
            return func.min(value)
        case Operation.maximum:
            return func.max(value)
        case Operation.mean:
            return func.avg(value)
        case _:
            e = OperationError("Operación invalida. Debe ser de tipo enum.Enum: Operation")
            return e.msj_error


def operation(patient_id: str, db: Session, operation: Operation, value: float, model):
    """
    **Get the mean, minimum or maximum value of blood sugar**

    """
    selected_operation = select_operation(operation, value)
    stmt = select(selected_operation).where(model.patient_id == patient_id)
    result = db.scalar(stmt)
    detail_error = f"The patient with id {patient_id} has no records"
    exception_if_not_exists(result, detail_error)
    return result


def make_analize(patient_id: str, db: Session, value: float, model):
    """De vuelve el mínimo, máximo y media"""

    minimum = operation(patient_id, db, Operation.minimum, value, model)
    maximum = operation(patient_id, db, Operation.maximum, value, model)
    mean = operation(patient_id, db, Operation.mean, value, model)
    return (minimum, maximum, mean)
