from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from dependencies.dependencies import get_db
from models.models import Doctor, Email
from schemas.schemas import DoctorIn, DoctorOut, DoctorUp, EmailSchema
from routes.jwt_oauth_doctor import get_password_hash, get_current_user, verify_password
from sendemail.sendemail import send_email

router = APIRouter(prefix="/doctor", tags=["Doctors"])


@router.post("/register")
def register_doctor(
    doctor: DoctorIn,
    db: Session = Depends(get_db),
):
    """**Register a new doctor**

    If you submit an email address, a verification code will be sent to your inbox.
    """
    stmt = select(Doctor).where(Doctor.id == doctor.id)
    result = db.scalars(stmt).first()
    if result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "Doctor already exists", "id": doctor.id},
        )
    doctor_bd = doctor.__dict__
    doctor_bd.update(password=get_password_hash(doctor_bd["password"]))
    if doctor_bd["email_address"]:
        code = send_email(doctor_bd["first_name"], doctor_bd["email_address"])
        email = EmailSchema(
            email_address=doctor_bd["email_address"], doctor_id=doctor_bd["id"], code=code
        ).model_dump()
        db.add(Email(**email))
    del doctor_bd["email_address"]
    db.add(Doctor(**doctor_bd))
    db.commit()
    return JSONResponse({"message": "Doctor registration successful", "id": doctor.id})


@router.get("/me", response_model=DoctorOut)
def get_doctor(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """**Get information about the currently authenticated doctor**"""
    doctor_data = current_doctor.__dict__
    doctor = {key: value for key, value in doctor_data.items() if value is not None or key == "password"}
    stmt = select(Email).where(Email.doctor_id == current_doctor.id)
    email = db.scalars(stmt).first()
    doctor["email_address"] = email.email_address
    doctor["email_verify"] = email.email_verify
    return DoctorOut(**doctor)


@router.put("/update")
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
    stmt = select(Doctor).where(Doctor.id == current_doctor.id)
    result = db.scalars(stmt).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Doctor not found", "id": doctor.id},
        )
    if doctor.id == "null" or doctor.first_name == "null":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "You must provide a valid data for first_name and id"},
        )

    doctor_data = doctor.model_dump(exclude_unset=True)
    updated_data = {key: value for key, value in doctor_data.items()}
    if updated_data.get("email_address"):
        if updated_data.get("first_name"):
            name = updated_data["first_name"]
        else:
            name = result.first_name
        if updated_data.get("id"):
            id = updated_data["id"]
        else:
            id = result.id
        stmt = select(Email).where(Email.doctor_id == current_doctor.id)
        email_bd = db.scalar(stmt).email_address
        if email_bd != updated_data["email_address"]:
            code = send_email(name, updated_data["email_address"])
            email = EmailSchema(
                email_address=updated_data["email_address"], doctor_id=id, email_verify=False, code=code
            ).model_dump()
            stmt = update(Email).where(Email.doctor_id == current_doctor.id).values(**email)
            db.execute(stmt)
        del updated_data["email_address"]
    if doctor.password and not verify_password(doctor.password, result.password):
        updated_data.update(password=get_password_hash(doctor.password))
    else:
        updated_data.update(password=result.password)
    stmt = update(Doctor).where(Doctor.id == current_doctor.id).values(**updated_data)
    db.execute(stmt)
    db.commit()
    return JSONResponse({"message": "Doctor data was updated successfully."})


@router.delete("/delete")
def delete_doctor(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """**Delete the currently authenticated doctor**"""
    stmt = delete(Doctor).where(Doctor.id == current_doctor.id)
    db.execute(stmt)
    db.commit()
    return JSONResponse({"message": f"Doctor with ID {current_doctor.id} has been successfully deleted."})
