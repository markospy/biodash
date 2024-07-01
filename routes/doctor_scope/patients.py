from datetime import datetime
from random import randint
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Security, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import asc, between, delete, desc, distinct, func, select, update
from sqlalchemy.orm import Session

from dependencies.dependencies import get_db
from models.enumerations import FilterBy, Order, SortBy
from models.exceptions import exception_if_already_exists, exception_if_not_exists
from models.models import Address, Doctor, Patient, doctor_patient
from routes.oauth import get_current_user
from schemas.schemas import PatientSchema, PatientSchemeList, PatientUp

from ..oauth import get_password_hash

router = APIRouter(prefix="/patients", tags=["Patients"])


def get_patient_by_id_and_doctor_id(patient_id, doctor_id, db: Session):
    """Get patient by ID"""

    stmt = select(Patient).join(Patient.doctors).where(Patient.id == patient_id, Doctor.id == doctor_id)
    patient_db = db.scalars(stmt).first()
    return patient_db


def get_patient_by_id(id, db: Session):
    stmt = select(Patient).where(Patient.id == id)
    patient_db = db.scalar(stmt)
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


def add_patient_bd(patient_id, patient_password, doctor_id, db: Session):
    smt = doctor_patient.insert().values(patient_id=patient_id, doctor_id=doctor_id)
    db.execute(smt)
    db.commit()
    if not patient_password:
        return JSONResponse(content={"message": "Patient registration successful", "id": patient_id}, status_code=201)
    return JSONResponse(
        content={"message": "Patient registration successful", "id": patient_id, "password": patient_password},
        status_code=201,
    )


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


def choice_filter(
    filter_by, range: list[int] | None = None, birth_date: list[datetime] | None = None, value: int | str = None
):
    match filter_by:
        case "first name":
            filter = Patient.first_name == value
        case "last name":
            filter = Patient.last_name == value
        case "birth date":
            if value:
                filter = Patient.birth_date = value
            else:
                filter = between(Patient.birth_date, birth_date[0], birth_date[1])
        case "height":
            if value:
                filter = Patient.height = value
            else:
                filter = between(Patient.height, range[0], range[1])
        case "weight":
            if value:
                filter = Patient.weight = value
            else:
                filter = between(Patient.weight, range[0], range[1])
        case "scholing":
            filter = Patient.scholing == value
        case "employee":
            filter = Patient.employee == value
        case SortBy.married:
            filter = Patient.married == value
        case "gender":
            filter = Patient.gender == value
    return filter


def choice_order_by(order_by):
    match order_by:
        case "first name":
            filter = Patient.first_name
        case "last name":
            filter = Patient.last_name
        case "birth date":
            filter = Patient.birth_date
        case "height":
            filter = Patient.height
        case "weight":
            filter = Patient.weight
        case "scholing":
            filter = Patient.scholing
        case "employee":
            filter = Patient.employee
        case SortBy.married:
            filter = Patient.married
        case "gender":
            filter = Patient.gender
    return filter


@router.post("")
def add_patient(
    current_doctor: Annotated[Doctor, Security(get_current_user, scopes=["doctor"])],
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
        return add_patient_bd(patient_id, None, current_doctor.id, db)
    else:
        patient_db = get_patient_by_id(patient.id, db)
        patient_exist_alert(patient_db)
        patient_dict = patient.model_dump(exclude_unset=True)
        patient_dict = check_and_add_address(patient_dict, db)
        password = patient_dict["first_name"] + "_" + str(randint(10_000, 99_999))
        patient_dict["password"] = get_password_hash(password)
        db.add(Patient(**patient_dict))
        return add_patient_bd(patient_dict["id"], password, current_doctor.id, db)


@router.get("", response_model=PatientSchemeList)
def get_patient(
    current_doctor: Annotated[Doctor, Security(get_current_user, scopes=["doctor"])],
    filter_by: FilterBy = "first_name",
    value: int | str | datetime = None,
    range_min: int | None = None,
    range_max: int | None = None,
    birth_date_min: datetime = Query(
        description="Establece el limite inferior de un rango  de fecha para filtrar por fecha.",
        default=datetime(1950, 1, 1),
    ),
    birth_date_max: datetime = Query(
        description="Establece el limite superior de un rango  de fecha para filtrar por fecha.",
        default=datetime(2025, 1, 1),
    ),
    order_by: SortBy = "last name",
    order: Order = "asc",
    limit: int | None = None,
    offset: int | None = None,
    db: Session = Depends(get_db),
):
    """**Gets a patient** with their id or a **list of them** using a set of filters and sort order

    *Args:*

        filter_by: Criterio de filtrado (obligatorio). Puede ser: first_name, last_name, birth_date, gender, height, weight, scholing, employee o married. Por defecto es first_name.

        value: Valor a aplicar al filtro (opcional). Puede ser un número entero, una cadena de texto o una fecha. Si se configura, se ignorara el filtrado por rango.

        range_min y range_max: Límites inferior y superior para filtrar por rango de valores (opcional).

        birth_date_min y birth_date_max: Límites inferior y superior para filtrar por rango de fechas de nacimiento (opcional). Por defecto, el límite inferior es el 1 de enero de 1950 y el límite superior es el 1 de enero de 2025.

        order_by: Criterio de ordenamiento (opcional). Puede ser: first_name, last_name, birth_date, gender, height, weight, scholing, employee o married. Por defecto es last name.

        order: Orden de ordenamiento (opcional). Puede ser asc (ascendente) o desc (descendente). Por defecto es asc.

        limit: Tamaño de la salida (opcional). Por defecto es todos los pacientes.

        offset: Posición inicial de la lista (opcional). Por defecto es 0.

        Descripción:

        Este endpoint devuelve una lista de pacientes que coinciden con los criterios de filtrado y ordenamiento especificados. Si no se proporciona ningún parámetro de consulta, se devuelve la lista completa de pacientes.

    """
    filter = choice_filter(
        filter_by, range=[range_min, range_max], birth_date=[birth_date_min, birth_date_max], value=value
    )
    order_critery = choice_order_by(order_by)

    len = (
        db.query(func.count(distinct(Patient.id)))
        .select_from(Patient)
        .where(Doctor.id == current_doctor.id, filter)
        .scalar()
    )

    order_query = asc
    if order == "desc":
        order_query = desc

    stmt = (
        select(Patient)
        .join(Patient.doctors)
        .where(Doctor.id == current_doctor.id, filter)
        .order_by(order_query(order_critery))
        .offset(offset)
        .limit(limit)
    )

    patients_db = db.scalars(stmt).all()
    exception_if_not_exists(patients_db, "Patients no fount")

    patients_list = []
    for patient_db in patients_db:
        patient_db = patient_db.__dict__
        if patient_db.get("address_id"):
            stmt = select(Address).where(Address.id == patient_db.get("address_id"))
            address = db.scalars(stmt).first()
            if address:
                patient_db["address"] = address.address
        patients_list.append(PatientSchema(**patient_db))
    return PatientSchemeList(len=len, patients=patients_list)


@router.get("/{patient_id}", response_model=PatientSchema)
def get_patient(
    current_doctor: Annotated[Doctor, Security(get_current_user, scopes=["doctor"])],
    patient_id: str,
    db: Session = Depends(get_db),
):
    patient_db = get_patient_by_id_and_doctor_id(patient_id, current_doctor.id, db)
    exception_if_not_exists(patient_db, "This patient does not exist.")
    patient_db_dict = patient_db.__dict__.copy()
    if patient_db_dict["address_id"]:
        stmt = select(Address).where(Address.id == patient_db_dict["address_id"])
        address = db.scalars(stmt).first()
        if address:
            patient_db_dict["address"] = address.address
    return PatientSchema(**patient_db_dict)


@router.put("")
def update_patient(
    current_doctor: Annotated[Doctor, Security(get_current_user, scopes=["doctor"])],
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
    stmt = select(Patient).join(Patient.doctors).where(Patient.id == patient_id, Doctor.id == current_doctor.id)
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

    stmt = update(Patient).where(Patient.id == patient_id).values(**patient_dict)
    if patient_dict.get("id"):
        db.execute(
            doctor_patient.update()
            .where(doctor_patient.c.patient_id == patient_id)
            .values(patient_id=patient_dict["id"], doctor_id=current_doctor.id)
        )
    db.execute(stmt)
    db.commit()
    return JSONResponse(f"The info of the patient {patient.id} has been changed successfully.")


@router.delete("/{patient_id}")
def delete_patient(
    current_doctor: Annotated[Doctor, Security(get_current_user, scopes=["doctor"])],
    patient_id: str,
    db: Session = Depends(get_db),
):
    stmt = select(Patient).join(Patient.doctors).where(Patient.id == patient_id, Doctor.id == current_doctor.id)
    patient_db = db.scalars(stmt).first()
    if not patient_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This patient does not exist.",
        )

    stmt = doctor_patient.select().where(doctor_patient.c.patient_id == patient_id)
    result = len(db.scalars(stmt).all())
    if result == 1:
        stmt = delete(Patient).where(Patient.id == patient_id)
        db.execute(stmt)

    stmt = doctor_patient.delete().where(
        doctor_patient.c.patient_id == patient_id, doctor_patient.c.doctor_id == current_doctor.id
    )
    db.execute(stmt)
    db.commit()
    return JSONResponse(f"The user patient {patient_id} has been successfully deleted.")
