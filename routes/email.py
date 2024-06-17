from typing import Annotated

from fastapi import APIRouter, Depends, status, Security
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from dependencies.dependencies import get_db
from models.models import Doctor, Email
from routes.oauth import get_current_user
from sendemail.sendemail import send_email

router = APIRouter(prefix="/email_verification", tags=["Email verification"])


@router.post("/{code}")
def send_code(
    code: int,
    current_doctor: Annotated[Doctor, Security(get_current_user, scopes=["doctor"])],
    db: Session = Depends(get_db),
):
    """**Verify the email of the authenticated doctor with the code sent to the email**"""
    stmt = select(Email).where(Email.doctor_id == current_doctor.id)
    email_bd = db.scalars(stmt).first()
    if email_bd.email_verify:
        return JSONResponse(content={"message": "The email is already verified"})
    if code != email_bd.code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "The code is invalid"})
    stmt = update(Email).where(Email.doctor_id == current_doctor.id).values(email_verify=True)
    db.execute(stmt)
    db.commit()
    return JSONResponse(content={"message": "The email is already verified"})


@router.get("")
def request_code(
    current_doctor: Annotated[Doctor, Security(get_current_user, scopes=["doctor"])],
    db: Session = Depends(get_db),
):
    """**Send a new validation email to the doctor's registered email**"""
    stmt = select(Email).where(Email.doctor_id == current_doctor.id)
    email_bd = db.scalars(stmt).first()
    if email_bd.email_verify:
        return JSONResponse(content={"message": "The email is already verified"})
    code = send_email(current_doctor.first_name, email_bd.email_address)
    stmt = update(Email).where(Email.doctor_id == current_doctor.id).values(code=code)
    db.execute(stmt)
    db.commit()
    return JSONResponse(content={"message": "A new verification code has been sent to your inbox"})
