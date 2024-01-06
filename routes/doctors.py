from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from dependencies.dependencies import get_db
from models.models import Doctor
from schemas.schemas import DoctorIn, DoctorOut, DoctorUp
from routes.jwt_oauth_doctor import get_password_hash, get_current_user, verify_password

router = APIRouter(prefix="/doctor", tags=["Doctors"])


@router.post("/register")
def register_doctor(
    doctor: DoctorIn,
    db: Session = Depends(get_db),
):
    """
    ## Register a Doctor

    ### `POST /doctor/register`

    Register a new doctor.

    #### Request Body:

    ```json
    {
    "doctor_id": "string",
    "first_name": "string",
    "second_name": "string",
    "last_name": "string",
    "specialty": "string",
    "password": "string",
    "portrait": "string"
    }
    ```

    #### Responses:

        201 Created: Doctor registered successfully.

    ```json
    {
    "message": "Doctor registration successful",
    "doctor_id": "string"
    }
    ```

        409 Conflict: Doctor with the provided ID already exists.

    ```json
    {
    "error": "Doctor already exists",
    "doctor_id": "string"
    }
    ```

    """
    stmt = select(Doctor).where(Doctor.doctor_id == doctor.doctor_id)
    result = db.scalars(stmt).first()
    if result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "Doctor already exists", "doctor_id": doctor.doctor_id},
        )
    doctor_bd = doctor.__dict__
    doctor_bd.update(password=get_password_hash(doctor_bd["password"]))
    db.add(Doctor(**doctor_bd))
    db.commit()
    return JSONResponse({"message": "Doctor registration successful", "doctor_id": doctor.doctor_id})


@router.get("/me", response_model=DoctorOut)
def get_doctor(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Get Current Doctor Information

    `GET /doctor/me`

    Get information about the currently authenticated doctor.
    #### Responses:

        200 OK: Doctor information retrieved successfully.

    ```json
    {
    "doctor_id": "string",
    "first_name": "string",
    "second_name": "string",
    "last_name": "string",
    "specialty": "string",
    "portrait": "string"
    }
    ```
    """
    doctor_data = current_doctor.__dict__
    updated_data = {key: value for key, value in doctor_data.items() if value is not None or key == "password"}
    return DoctorOut(**updated_data)


@router.put("/update")
def update_doctor(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    doctor: DoctorUp,
    db: Session = Depends(get_db),
):
    """
    Update Doctor Information

    `PUT /doctor/update`

    Update information about the currently authenticated doctor.

    #### Request Body:

    ```json
    {
    "first_name": "string",
    "second_name": "string",
    "last_name": "string",
    "specialty": "string",
    "password": "string",
    "portrait": "string"
    }
    ```

    #### Responses:

        200 OK: Doctor information updated successfully.

    ```json
    {
    "message": "Doctor data was updated successfully."
    }
    ```

        404 Not Found: Doctor with the provided ID not found.

    ```json
    {
    "error": "Doctor not found",
    "doctor_id": "string"
    }
    ```
    """
    stmt = select(Doctor).where(Doctor.doctor_id == current_doctor.doctor_id)
    result = db.scalars(stmt).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Doctor not found", "doctor_id": doctor.doctor_id},
        )
    # Utiliza el modelo Pydantic para validar y normalizar los datos
    doctor_data = doctor.model_dump(exclude_unset=True)  # Excluye valores no establecidos
    updated_data = {key: value for key, value in doctor_data.items()}
    # Verificar si la nueva contraseña es diferente de la antigua
    if doctor.password and not verify_password(doctor.password, result.password):
        updated_data.update(password=get_password_hash(doctor.password))
    else:
        updated_data.update(password=result.password)
    stmt = update(Doctor).where(Doctor.doctor_id == current_doctor.doctor_id).values(**updated_data)
    db.execute(stmt)
    db.commit()
    return JSONResponse({"message": "Doctor data was updated successfully."})


@router.delete("/delete")
def delete_doctor(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Delete Doctor

    `DELETE /doctor/delete`

    Delete the currently authenticated doctor.

    #### Responses:

        200 OK: Doctor deleted successfully.

    ```json
    {
    "message": "Doctor with ID {doctor_id} has been successfully deleted."
    }
    ```
    """
    stmt = delete(Doctor).where(Doctor.doctor_id == current_doctor.doctor_id)
    db.execute(stmt)
    db.commit()
    return JSONResponse({"message": f"Doctor with ID {current_doctor.doctor_id} has been successfully deleted."})
