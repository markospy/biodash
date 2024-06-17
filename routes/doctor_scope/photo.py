from typing import Annotated
import os
from PIL import Image

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, Security
from fastapi.responses import JSONResponse

from sqlalchemy import update
from sqlalchemy.orm import Session

from models.models import Doctor
from routes.oauth import get_current_user
from dependencies.dependencies import get_db
from schemas.schemas import DoctorPhoto

router = APIRouter(prefix="/doctor", tags=["Avatar"])

PATH_PHOTOS = os.path.abspath("photos/") + "/"


def create_avatar(filename: str, doctor_id: str):
    size_define = 300, 300
    image = Image.open(PATH_PHOTOS + filename, mode="r")
    image.thumbnail(size_define)
    image = image.convert("RGB")
    image.save(PATH_PHOTOS + doctor_id + ".png")
    os.remove(PATH_PHOTOS + filename)


@router.post("/upload_photo")
async def upload_photo(
    current_doctor: Annotated[Doctor, Security(get_current_user, scopes=["doctor"])],
    background_task: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """**Upload a photo for the doctor's profile**"""
    with open(PATH_PHOTOS + file.filename, "wb") as photo:
        content = await file.read()
        photo.write(content)
        photo.close()

    background_task.add_task(create_avatar, filename=file.filename, doctor_id=current_doctor.id)
    stmt = (
        update(Doctor)
        .where(Doctor.id == current_doctor.id)
        .values(
            DoctorPhoto(
                id=current_doctor.id,
                first_name=current_doctor.first_name,
                last_name=current_doctor.last_name,
                specialty=current_doctor.specialty,
                portrait=current_doctor.id + ".png",
            ).model_dump(exclude_unset=True)
        )
    )
    db.execute(stmt)
    db.commit()
    return JSONResponse(content={"message": "success"})
