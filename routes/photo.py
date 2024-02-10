from typing import Annotated
from os import getcwd, remove
from PIL import Image

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy import update
from sqlalchemy.orm import Session

from models.models import Doctor
from routes.jwt_oauth_doctor import get_current_user
from dependencies.dependencies import get_db
from schemas.schemas import DoctorPhoto

router = APIRouter(prefix="/doctor", tags=["Avatar"])

PATH_PHOTOS = getcwd() + "/photos/"


def create_avatar(filename: str, doctor_id: str):
    size_define = 300, 300
    image = Image.open(PATH_PHOTOS + filename, mode="r")
    image.thumbnail(size_define)
    image.save(PATH_PHOTOS + doctor_id + "." + filename.split(".")[-1])
    remove(PATH_PHOTOS + filename)
    print("success")


@router.post("/upload_photo/")
async def upload_photo(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    background_task: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    with open(PATH_PHOTOS + file.filename, "wb") as photo:
        content = await file.read()
        photo.write(content)
        photo.close()

    background_task.add_task(
        create_avatar, filename=file.filename, doctor_id=current_doctor.id
    )
    stmt = (
        update(Doctor)
        .where(Doctor.id == current_doctor.id)
        .values(
            DoctorPhoto(
                id=current_doctor.id,
                first_name=current_doctor.first_name,
                portrait="/photos/"
                + current_doctor.id
                + "."
                + file.filename.split(".")[-1],
            ).model_dump(exclude_unset=True)
        )
    )
    db.execute(stmt)
    db.commit()
    return JSONResponse(content={"message": "success"})