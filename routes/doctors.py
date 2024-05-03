from typing import Annotated
import os

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from dependencies.dependencies import get_db
from models.models import Doctor, Email
from schemas.schemas import (
    DoctorIn,
    DoctorOut,
    DoctorPhoto,
    DoctorUp,
    EmailSchema,
)
from routes.oauth import get_password_hash, get_current_user, verify_password
from sendemail.sendemail import send_email
from models.exceptions import exception_if_already_exists

router = APIRouter(prefix="/doctor", tags=["Doctors"])


def update_doctor_photo(doctor: Doctor, new_id: int, db: Session):
    """Update doctor photo"""
    if doctor.id:
        path_photo = os.path.abspath("photos/")
        os.rename(
            f"{path_photo}/{doctor.id}.png",
            f"{path_photo}/{new_id}.png",)
        stmt = (
            update(Doctor)
            .where(Doctor.id == doctor.id)
            .values(
                DoctorPhoto(
                    id=new_id,
                    first_name=doctor.first_name,
                    portrait=new_id + ".png",
                ).model_dump(exclude_unset=True)
            )
        )
        db.execute(stmt)

def update_doctor_email(current_doctor: Doctor, data: dict, db: Session,):
    """Update doctor email"""
    if data.get("email_address"):
        stmt = select(Email).where(Email.doctor_id == current_doctor.id)
        email_bd = db.scalar(stmt).first()
        if email_bd:
            email_bd = email_bd.email_address
        if email_bd != data["email_address"]:
            code = send_email(data["first_name"],data["email_address"])
            email = EmailSchema(
                email_address=data["email_address"],
                doctor_id=id,
                email_verify=False,
                code=code,
            ).model_dump()
            if email_bd:
                stmt = (
                    update(Email)
                    .where(Email.doctor_id == current_doctor.id)
                    .values(**email)
                )
                db.execute(stmt)
            else:
                db.add(Email(**email))
        del data["email_address"]

def get_doctor_by_id(id, db: Session):
    """Get doctor by ID"""
    stmt = select(Doctor).where(Doctor.id == id)
    doctor_db = db.scalars(stmt).first()
    return doctor_db

def set_email_information(doctor: dict, email: Email | None):
    """Set email information for the doctor"""
    if email:
        doctor["email_address"] = email.email_address
        doctor["email_verify"] = email.email_verify
    else:
        doctor["email_address"] = None
        doctor["email_verify"] = False

def update_doctor_info(new_data:str | int | None, current_data:str | int | None):
    if new_data == None or new_data != current_data:
        return current_data

def get_url(request: Request, end_point_function: str):
    """Devuelve la url raíz del servicio"""
    url = request.url_for(end_point_function)
    return str(url)[:-6]

def get_url_photo(doctor: Doctor, request: Request, db: Session, end_point: str):
    """**Get the doctor's profile photo url**"""
    stmt = select(Doctor).where(Doctor.id == doctor.id)
    portait_url = db.scalars(stmt).first().portrait
    if not portait_url:
        return
    url = get_url(request, end_point) + "photos/" + portait_url
    return url


@router.post("", status_code=status.HTTP_201_CREATED)
def register_doctor(doctor: DoctorIn, db: Session = Depends(get_db)):
    """**Register a new doctor**

    If you submit an email address, a verification code will be sent to your inbox.
    """
    doctor_db = get_doctor_by_id(doctor.id, db)
    exception_if_already_exists(doctor_db, {"error": "Doctor already exists", "id": doctor.id})
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
def get_doctor(current_doctor: Annotated[Doctor, Depends(get_current_user)], request: Request, db: Session = Depends(get_db)):
    """**Get information about the currently authenticated doctor**"""
    doctor_data = current_doctor.__dict__
    doctor = {key: value for key, value in doctor_data.items() if value is not None or key == "password"}
    doctor['photo'] = get_url_photo(current_doctor, request, db, "get_doctor")
    stmt = select(Email).where(Email.doctor_id == current_doctor.id)
    email = db.scalars(stmt).first()
    set_email_information(doctor, email)
    return DoctorOut(**doctor)


@router.put("", status_code=status.HTTP_200_OK)
def update_doctor(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
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
    doctor_data = doctor.model_dump(exclude_unset=True)
    updated_data = {key: value for key, value in doctor_data.items()}

    update_doctor_photo(current_doctor, new_id=doctor.id, db=db)
    updated_data['id'] = update_doctor_info(doctor.id, current_doctor.id)
    updated_data['first_name'] = update_doctor_info(doctor.first_name, current_doctor.first_name)

    if not verify_password(doctor.password, current_doctor.password):
        #Si es la misma contraseña no la sobreescribe en la base de datos
        updated_data['password'] = update_doctor_info(doctor.password, current_doctor.password)

    update_doctor_email(current_doctor, updated_data, db)
    stmt = (update(Doctor).where(Doctor.id == current_doctor.id).values(**updated_data))
    db.execute(stmt)
    db.commit()
    return JSONResponse({"message": "Doctor data was updated successfully."})

@router.delete("", status_code=status.HTTP_200_OK)
def delete_doctor(current_doctor: Annotated[Doctor, Depends(get_current_user)], db: Session = Depends(get_db)):
    """**Delete the currently authenticated doctor**"""
    stmt = delete(Doctor).where(Doctor.id == current_doctor.id)
    db.execute(stmt)
    db.commit()
    return JSONResponse(
        {
            "message": f"Doctor with ID {current_doctor.id} has been successfully deleted."
        }
    )