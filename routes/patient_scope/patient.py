from typing import Annotated

from fastapi import APIRouter, Depends, Security, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from models.models import Patient, Address, doctor_patient
from dependencies.dependencies import get_db
from schemas.schemas import PatientSchema, PatientUp
from routes.oauth import get_password_hash, get_current_user


router = APIRouter(prefix="/patient", tags=["Patient Access: Your Information"])


def get_patient_by_id(id, db: Session):
    stmt = select(Patient).where(Patient.id == id)
    patient_db = db.scalar(stmt)
    return patient_db


@router.get("/", response_model=PatientSchema)
def get_patient(
    current_patient: Annotated[Patient, Security(get_current_user, scopes=["patient"])],
    db: Session = Depends(get_db),
):
    patient_db = get_patient_by_id(current_patient.id, db)
    patient_db_dict = patient_db.__dict__.copy()
    if patient_db_dict["address_id"]:
        stmt = select(Address).where(Address.id == patient_db_dict["address_id"])
        address = db.scalars(stmt).first()
        if address:
            patient_db_dict["address"] = address.address
    return PatientSchema(**patient_db_dict)


@router.put("")
def update_patient(
    current_patient: Annotated[Patient, Security(get_current_user, scopes=["patient"])],
    patient: PatientUp,
    db: Session = Depends(get_db),
):
    """**Modify patient information**. Unconfigured values will not be changed.

    If you put the string 'null' as the value of any parameter, the corresponding field
    in the database will be set to Null. It is useful to eliminate incorrect data from
    the database. A value of 'null' will not be accepted for first_name or id.

    Args:

        patient_id (str): Patient id.
    """
    stmt = select(Patient).join(Patient.doctors).where(Patient.id == current_patient.id)
    patient_db = db.scalars(stmt).first()
    if not patient_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This patient is not registered",
        )

    if patient.id == None or patient.first_name == None:
        patient.id = patient_db.id
        patient.first_name = patient_db.first_name

    patient_dict = patient.model_dump(exclude_unset=True)
    patient_dict["password"] = get_password_hash(patient_dict["password"])
    if patient_dict.get("address"):
        address_db = db.scalars(select(Address).where(Address.address == patient_dict["address"])).first()
        if not address_db:
            address = Address(address=patient_dict["address"])
            db.add(address)
            db.flush()
            patient_dict["address_id"] = address.id
        else:
            patient_dict["address_id"] = address_db.id
    else:
        stmt = select(Address).where(Address.id == patient_db.address_id)
        address = db.scalars(stmt).first()
        patient_dict["address"] = address.id
    del patient_dict["address"]

    stmt = update(Patient).where(Patient.id == current_patient.id).values(**patient_dict)
    if patient_dict.get("id"):
        db.execute(
            doctor_patient.update()
            .where(doctor_patient.c.patient_id == current_patient.id)
            .values(patient_id=current_patient.id)
        )
    db.execute(stmt)
    db.commit()
    return JSONResponse(f"The info of the patient {patient.id} has been changed successfully.")
