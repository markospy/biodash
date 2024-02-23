from typing import Annotated
from enum import Enum

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select, delete, update, and_, asc, desc
from sqlalchemy.orm import Session

from models.models import Patient, Doctor, Address, doctor_patient
from dependencies.dependencies import get_db
from schemas.schemas import PatientSchema, PatientUp
from routes.jwt_oauth_doctor import get_current_user


router = APIRouter(prefix="/patients", tags=["Patients"])


class SortBy(Enum):
    first_name = "first_name"
    second_name = "second_name"
    last_name = "last_name"
    birth_date = "birth_date"
    gender = "gender"
    height = "height"
    weight = "weight"
    scholing = "scholing"
    employee = "employee"
    married = "married"


class Order(Enum):
    asc = "asc"
    desc = "desc"


@router.post("/add")
def add_patient(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    patient: PatientSchema,
    db: Session = Depends(get_db),
):
    """**Add a new patient**

    If a patient with the same ID already exists in another doctor's office,
    you will be asked to add it from the 'add existing patient' endpoint
    """
    stmt = (
        select(Patient)
        .join(Patient.doctors)
        .where(and_(Patient.id == patient.id, Doctor.id == current_doctor.id))
    )
    patient_db = db.scalars(stmt).first()
    if patient_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This patient already exists.",
        )

    stmt = select(Patient).where(Patient.id == patient.id)
    patient_db = db.scalars(stmt).first()
    if patient_db:
        return JSONResponse(
            {
                "message": f"There is already a patient with id {patient.id} belonging to another doctor. Please check if this is the correct data and add it to your patient record.",
                "patient": f"{PatientSchema(**patient_db.__dict__)}",
            },
            status_code=status.HTTP_226_IM_USED,
        )

    patient_dict = patient.model_dump(exclude_unset=True)
    if patient_dict.get("address"):
        address_db = db.scalars(
            select(Address).where(Address.address == patient_dict["address"])
        ).first()
        if not address_db:
            address = Address(address=patient_dict["address"])
            db.add(address)
            db.flush()
            patient_dict["address_id"] = address.id
        else:
            patient_dict["address_id"] = address_db.id
    else:
        patient_dict["address_id"] = None
    del patient_dict["address"]
    db.add(Patient(**patient_dict))
    db.execute(
        doctor_patient.insert().values(
            patient_id=patient_dict["id"], doctor_id=current_doctor.id
        )
    )
    db.commit()
    return JSONResponse(
        {"message": "Patient registration successful", "id": patient_dict["id"]}
    )


@router.post("/add_existing_patient")
def add_patient(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    patient_id: str,
    db: Session = Depends(get_db),
):
    """Adds a patient who already belonged to another doctor's office to the currently verified doctor's office.
    Now the patient will belong to several doctors, depending on the number of doctors who have added them to their
    consultation.
    """
    stmt = (
        select(Patient)
        .join(Patient.doctors)
        .where(and_(Patient.id == patient_id, Doctor.id == current_doctor.id))
    )
    patient_db = db.scalars(stmt).first()
    if patient_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This patient is already registered.",
        )

    stmt = select(Patient).where(Patient.id == patient_id)
    patient_db = db.scalars(stmt).first()
    if not patient_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This patient does not exist.",
        )

    stmt = doctor_patient.insert().values(
        patient_id=patient_id, doctor_id=current_doctor.id
    )
    db.execute(stmt)
    db.commit()
    return JSONResponse(
        {"message": "Patient registration successful", "id": patient_id}
    )


@router.get("/patient", response_model=list[PatientSchema])
def get_patient(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    patient_id: str | None = None,
    filter_by: SortBy | None = None,
    limit: int | None = None,
    offset: int | None = None,
    order: Order | None = None,
    db: Session = Depends(get_db),
):
    """**Gets a patient** with their id or a **list of them** using a set of filters and sort order

    *Args:*

        patient_id (str | None, optional): Patient id. Defaults to None.

        filter_by (SortBy | None, optional): Sorting criteria: first_name, second_name, last_name, birth_date, height, weight, scholing, employee or married. Defaults to first_name.

        limit (int | None, optional): Output size. Defaults to all.

        offset (int | None, optional): Top of list. Defaults to 0.

        order (Order | None, optional): asc or desc. Defaults to desc.
    """
    if patient_id:
        stmt = (
            select(Patient)
            .join(Patient.doctors)
            .where(
                and_(Patient.id == patient_id, Doctor.id == current_doctor.id)
            )
        )
        patient_db = db.scalars(stmt).first()
        if not patient_db:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This patient is not registered",
            )
        patient_db = patient_db.__dict__
        if patient_db.get("address_id"):
            stmt = select(Address).where(Address.id == patient_db["address_id"])
            address = db.scalars(stmt).first()
            if address:
                patient_db["address"] = address.address
        return [PatientSchema(**patient_db)]

    match filter_by:
        case SortBy.first_name:
            filter = Patient.first_name
        case SortBy.second_name:
            filter = Patient.second_name
        case SortBy.last_name:
            filter = Patient.last_name
        case SortBy.birth_date:
            filter = Patient.birth_date
        case SortBy.height:
            filter = Patient.height
        case SortBy.weight:
            filter = Patient.weight
        case SortBy.scholing:
            filter = Patient.scholing
        case SortBy.employee:
            filter = Patient.employee
        case SortBy.married:
            filter = Patient.married
        case _:
            filter = Patient.first_name

    if order == Order.asc:
        stmt = (
            select(Patient)
            .join(Patient.doctors)
            .where(Doctor.id == current_doctor.id)
            .order_by(asc(filter))
            .offset(offset)
            .limit(limit)
        )
    else:
        stmt = (
            select(Patient)
            .join(Patient.doctors)
            .where(Doctor.id == current_doctor.id)
            .order_by(desc(filter))
            .offset(offset)
            .limit(limit)
        )

    patients_db = db.scalars(stmt).all()
    if not patients_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There are no registered patients",
        )
    patients_list = []
    for patient_db in patients_db:
        patient_db = patient_db.__dict__
        if patient_db.get("address_id"):
            stmt = select(Address).where(
                Address.id == patient_db.get("address_id")
            )
            address = db.scalars(stmt).first()
            if address:
                patient_db["address"] = address.address
        patients_list.append(PatientSchema(**patient_db))
    return patients_list


@router.put("/modify")
def update_patient(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    patient_id: str,
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
    stmt = (
        select(Patient)
        .join(Patient.doctors)
        .where(and_(Patient.id == patient_id, Doctor.id == current_doctor.id))
    )
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
    if patient_dict.get("address"):
        address_db = db.scalars(
            select(Address).where(Address.address == patient_dict["address"])
        ).first()
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

    stmt = (
        update(Patient).where(Patient.id == patient_id).values(**patient_dict)
    )
    if patient_dict.get("id"):
        db.execute(
            doctor_patient.update()
            .where(doctor_patient.c.patient_id == patient_id)
            .values(patient_id=patient_dict["id"], doctor_id=current_doctor.id)
        )
    db.execute(stmt)
    db.commit()
    return JSONResponse(
        f"The info of the patient {patient.id} has been changed successfully."
    )


@router.delete("/delete")
def delete_patient(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    patient_id: str,
    db: Session = Depends(get_db),
):
    stmt = (
        select(Patient)
        .join(Patient.doctors)
        .where(and_(Patient.id == patient_id, Doctor.id == current_doctor.id))
    )
    patient_db = db.scalars(stmt).first()
    if not patient_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This patient does not exist.",
        )

    stmt = doctor_patient.select().where(
        doctor_patient.c.patient_id == patient_id
    )
    result = len(db.scalars(stmt).all())
    if result == 1:
        stmt = delete(Patient).where(Patient.id == patient_id)
        db.execute(stmt)

    stmt = doctor_patient.delete().where(
        and_(
            doctor_patient.c.patient_id == patient_id,
            doctor_patient.c.doctor_id == current_doctor.id,
        )
    )
    db.execute(stmt)
    db.commit()
    return JSONResponse(
        f"The user patient {patient_id} has been successfully deleted."
    )
