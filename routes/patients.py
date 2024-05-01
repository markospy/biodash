from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select, delete, update, and_, asc, desc
from sqlalchemy.orm import Session

from models.models import Patient, Doctor, Address, doctor_patient
from dependencies.dependencies import get_db
from schemas.schemas import PatientSchema, PatientUp
from routes.oauth import get_current_user
from models.enumerations import Order, SortBy
from models.exceptions import exception_if_already_exists, exception_if_not_exists


router = APIRouter(prefix="/patients", tags=["Patients"])

def get_patient_by_id_and_doctor_id(patient_id, doctor_id, db: Session):
    """Get patient by ID"""

    stmt = select(Patient).join(Patient.doctors).where(and_(Patient.id == patient_id, Doctor.id == doctor_id))
    patient_db = db.scalars(stmt).first()
    return patient_db

def get_patient_by_id(id, db: Session):
    stmt = select(Patient).where(Patient.id == id)
    patient_db = db.scalars(stmt).first()
    return patient_db

def check_and_add_address(patient: dict, db: Session):
    if patient.get("address"):
        address_db = db.scalars(select(Address).where(Address.address == patient["address"])).first()
        if not address_db:
            address = Address(address=patient["address"])
            db.add(address)
            db.flush()
            patient["address_id"] = address.id
        else:
            patient["address_id"] = address_db.id
    del patient["address"]
    return patient

def add_patient_bd(patient_id, doctor_id, db: Session):
    smt = doctor_patient.insert().values(patient_id=patient_id, doctor_id=doctor_id)
    db.execute(smt)
    db.commit()
    return JSONResponse({"message": "Patient registration successful", "id": patient_id})

def patient_exist_alert(patient: dict):
    """Envia un alerta si el diccionario con los datos del paciente no esta vacio."""
    if patient:
        return JSONResponse(
            {
                "message": f"There is already a patient with id {patient.id} belonging to another doctor. Please check if this is the correct data and add it to your patient record.",
                "patient": f"{PatientSchema(**patient.__dict__)}",
            },
            status_code=status.HTTP_226_IM_USED,
        )

@router.post("")
def add_patient(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    patient: PatientSchema,
    isExist: bool = False,
    patient_id: str | None = None,
    db: Session = Depends(get_db),
):
    """
    **Add a new patient**

    If you want a patient linked to the office of another doctor, only,
    you must add the parameters _isExist = true_ and the _patient ID_, leaving
    in None the parameter _patient_

    """
    result = get_patient_by_id_and_doctor_id(patient.id, current_doctor.id, db)
    exception_if_already_exists(result, "This patient already exists.")

    if isExist:
        patient_db = get_patient_by_id(patient_id, db)
        exception_if_not_exists(patient_db, "This patient does not exist.")
        add_patient_bd(patient_id, current_doctor.id, db)
    else:
        patient_db = get_patient_by_id(patient.id, db)
        patient_exist_alert(patient_db)
        patient_dict = patient.model_dump(exclude_unset=True)
        patient_dict = check_and_add_address(patient_dict, db)
        db.add(Patient(**patient_dict))
        add_patient_bd(patient_dict["id"], current_doctor.id, db)


@router.get("", response_model=list[PatientSchema])
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


@router.put("")
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


@router.delete("")
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
