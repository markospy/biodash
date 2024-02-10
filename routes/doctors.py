from typing import Annotated
from os import rename

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
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
from routes.jwt_oauth_doctor import (
    get_password_hash,
    get_current_user,
    verify_password,
)
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
            email_address=doctor_bd["email_address"],
            doctor_id=doctor_bd["id"],
            code=code,
        ).model_dump()
        db.add(Email(**email))
    del doctor_bd["email_address"]
    db.add(Doctor(**doctor_bd))
    db.commit()
    return JSONResponse(
        {"message": "Doctor registration successful", "id": doctor.id}
    )


@router.get("/me", response_model=DoctorOut)
def get_doctor(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """**Get information about the currently authenticated doctor**"""
    doctor_data = current_doctor.__dict__
    doctor = {
        key: value
        for key, value in doctor_data.items()
        if value is not None or key == "password"
    }
    stmt = select(Email).where(Email.doctor_id == current_doctor.id)
    email = db.scalars(stmt).first()
    if email:
        doctor["email_address"] = email.email_address
        doctor["email_verify"] = email.email_verify
    else:
        doctor["email_address"] = None
        doctor["email_verify"] = False
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
    if doctor.id:
        rename(
            f"/home/marcos/proyectos/backend/biodash/photos/{result.id}.png",
            f"/home/marcos/proyectos/backend/biodash/photos/{doctor.id}.png",
        )
    if doctor.id == None or doctor.first_name == None:
        doctor.id = result.id
        doctor.first_name = result.first_name

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
        email_bd = db.scalars(stmt).first()
        if email_bd:
            email_bd = email_bd.email_address
        if email_bd != updated_data["email_address"]:
            code = send_email(name, updated_data["email_address"])
            email = EmailSchema(
                email_address=updated_data["email_address"],
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
                stmt = db.add(Email(**email))
        del updated_data["email_address"]
    if doctor.password and not verify_password(
        doctor.password, result.password
    ):
        updated_data.update(password=get_password_hash(doctor.password))
    else:
        updated_data.update(password=result.password)
    stmt = (
        update(Doctor)
        .where(Doctor.id == current_doctor.id)
        .values(**updated_data)
    )
    db.execute(stmt)
    stmt = (
        update(Doctor)
        .where(Doctor.id == current_doctor.id)
        .values(
            DoctorPhoto(
                id=current_doctor.id,
                first_name=current_doctor.first_name,
                portrait="/avatar/" + current_doctor.id + ".png",
            ).model_dump(exclude_unset=True)
        )
    )
    db.execute(stmt)
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
    return JSONResponse(
        {
            "message": f"Doctor with ID {current_doctor.id} has been successfully deleted."
        }
    )


# ON DELETE CASCADE
# The desired effect was cascading deletion of patients when deleting a doctor record.
# However, when I delete a doctor, the patients that are no longer associated with the
# doctor that have just been deleted remain, since the record in the union table is
# deleted: doctor_patient
