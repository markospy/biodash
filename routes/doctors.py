from typing import Annotated
import os

from fastapi import APIRouter, Depends, Request, status, Security
from fastapi.responses import JSONResponse
from sqlalchemy import select, update, delete, distinct, func
from sqlalchemy.orm import Session

from dependencies.dependencies import get_db
from models.models import Email, Doctor, doctor_patient
from schemas.schemas import EmailSchema, DoctorIn, DoctorOut, DoctorUp


from routes.oauth import get_password_hash, get_current_user, verify_password
from sendemail.sendemail import send_email
from models.exceptions import exception_if_already_exists

router = APIRouter(prefix="/doctor", tags=["Doctors"])


def update_photo_name(doctor: Doctor, new_id: str | None, db: Session):
    """Update doctor photo"""
    if new_id:
        try:
            path_photo = os.path.abspath("photos/")
            os.rename(
                f"{path_photo}/{doctor.id}.png",
                f"{path_photo}/{new_id}.png",
            )
            return f"{new_id}.png"
        except FileNotFoundError:
            pass
    else:
        return None


def update_doctor_email(new_email: str | None, doctor: Doctor, db: Session, doctor_id: str | None = None):
    """Update doctor email"""
    if doctor_id:
        id = doctor_id
    else:
        id = doctor.id

    stmt = select(Email).where(Email.doctor_id == doctor.id)
    email_bd = db.scalars(stmt).first()

    code = email_bd.code
    email_verify = False

    if new_email == None:
        new_email = email_bd.email_address
        email_verify = email_bd.email_verify
    else:
        code = send_email(doctor.first_name, new_email)

    email = EmailSchema(email_address=new_email, doctor_id=id, email_verify=email_verify, code=code).model_dump()

    if email_bd.email_address:
        stmt = update(Email).where(Email.doctor_id == doctor.id).values(**email)
        db.execute(stmt)
    else:
        db.add(Email(**email))


def get_doctor_by_id(id, db: Session):
    """Get doctor by ID"""
    stmt = select(Doctor).where(Doctor.id == id)
    doctor_db = db.scalars(stmt).first()
    return doctor_db


def set_email_information(current_doctor: Doctor, db: Session):
    """Set email information for the doctor"""

    stmt = select(Email).where(Email.doctor_id == current_doctor.id)
    email = db.scalars(stmt).first()

    email_doctor = {}
    if email:
        email_doctor["email_address"] = email.email_address
        email_doctor["email_verify"] = email.email_verify
    else:
        email_doctor["email_address"] = None
        email_doctor["email_verify"] = False

    return email_doctor


def update_doctor_info(new_data: str | int | None, current_data: str | int | None):
    if new_data == None:
        return current_data
    return new_data


def update_password(new_password, old_password):
    if new_password:
        if not verify_password(new_password, old_password):
            # Si es la misma contraseña no la sobreescribe en la base de datos
            return get_password_hash(update_doctor_info(new_password, old_password))
    return old_password


def get_url(request: Request, end_point_function: str):
    """Devuelve la url raíz del servicio"""
    url = request.url_for(end_point_function)
    return str(url)[:-6]


def get_url_photo(doctor: Doctor, request: Request, db: Session, end_point: str):
    """**Get the doctor's profile photo url**"""
    stmt = select(Doctor).where(Doctor.id == doctor.id)
    portait = db.scalars(stmt).first()
    if portait:
        if not portait.portrait:
            return
        url = get_url(request, end_point) + "photos/" + portait.portrait
        return url
    return


@router.post("", status_code=status.HTTP_201_CREATED)
def register_doctor(doctor: DoctorIn, db: Session = Depends(get_db)):
    """**Register a new doctor**

    If you submit an email address, a verification code will be sent to your inbox.
    """
    doctor_db = get_doctor_by_id(doctor.id, db)
    exception_if_already_exists(doctor_db, {"detail": "Doctor already exists", "id": doctor.id})
    doctor_bd = doctor.__dict__
    doctor_bd.update(password=get_password_hash(doctor_bd["password"]))

    if doctor_bd["email_address"]:
        code = send_email(doctor_bd["first_name"], doctor_bd["email_address"])
        email = EmailSchema(
            email_address=doctor_bd["email_address"],
            doctor_id=doctor_bd["id"],
            code=code,
        ).model_dump()
        db.add(Email(**email))

    del doctor_bd["email_address"]
    db.add(Doctor(**doctor_bd))
    db.commit()
    return JSONResponse(content={"message": "Doctor registration successful", "id": doctor.id})


@router.get("", response_model=DoctorOut, status_code=status.HTTP_200_OK)
def get_doctor(
    current_doctor: Annotated[Doctor, Security(get_current_user, scopes=["doctor"])],
    request: Request,
    db: Session = Depends(get_db),
):
    """
    **Get information about the currently authenticated doctor**
    """
    doctor_data = current_doctor.__dict__
    doctor = {key: value for key, value in doctor_data.items() if value is not None}
    doctor["photo"] = get_url_photo(current_doctor, request, db, "get_doctor")
    doctor.update(set_email_information(current_doctor, db))
    patients = (
        db.query(func.count(distinct(doctor_patient.c.patient_id)))
        .select_from(doctor_patient)
        .where(doctor_patient.c.doctor_id == current_doctor.id)
        .scalar()
    )
    return DoctorOut(**doctor, patients=patients)


@router.put("", status_code=status.HTTP_200_OK)
def update_doctor(
    current_doctor: Annotated[Doctor, Security(get_current_user, scopes=["doctor"])],
    doctor: DoctorUp,
    db: Session = Depends(get_db),
):
    """
    **Update information about the currently authenticated doctor**

    If you put the string 'null' as the value of any parameter, the corresponding field
    in the database will be set to Null. It is useful to eliminate incorrect data from
    the database. A value of 'null' will not be accepted for first_name or id.

    If you update your email address, a verification code will be sent to your inbox.
    """
    updated_data = {}
    updated_data["id"] = update_doctor_info(doctor.id, current_doctor.id)
    updated_data["first_name"] = update_doctor_info(doctor.first_name, current_doctor.first_name)
    updated_data["last_name"] = update_doctor_info(doctor.last_name, current_doctor.last_name)
    updated_data["specialty"] = update_doctor_info(doctor.specialty, current_doctor.specialty)
    updated_data["portrait"] = update_photo_name(current_doctor, new_id=doctor.id, db=db)
    updated_data["password"] = update_password(doctor.password, current_doctor.password)

    if doctor.id or doctor.email_address:
        update_doctor_email(doctor.email_address, current_doctor, db, doctor.id)

    stmt = update(Doctor).where(Doctor.id == current_doctor.id).values(**updated_data)
    db.execute(stmt)
    db.commit()
    return JSONResponse({"message": "Doctor data was updated successfully."})


@router.delete("", status_code=status.HTTP_200_OK)
def delete_doctor(
    current_doctor: Annotated[Doctor, Security(get_current_user, scopes=["doctor"])],
    db: Session = Depends(get_db),
):
    """
    **Delete the currently authenticated doctor**
    """
    stmt = delete(Doctor).where(Doctor.id == current_doctor.id)
    db.execute(stmt)
    db.commit()
    return JSONResponse({"message": f"Doctor with ID {current_doctor.id} has been successfully deleted."})
