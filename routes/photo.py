from typing import Annotated
import os
from PIL import Image

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, Request
from fastapi import status
from fastapi.responses import JSONResponse, RedirectResponse

from sqlalchemy import update, select
from sqlalchemy.orm import Session

from models.models import Doctor
from routes.jwt_oauth_doctor import get_current_user
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

def get_url(request: Request, end_point_function: str):
    """Devuelve la url raíz del servicio"""
    url = request.url_for(end_point_function)
    return str(url)[:-12]

@router.post("/upload_photo")
async def upload_photo(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    background_task: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """**Upload a photo for the doctor's profile**"""
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
                portrait=current_doctor.id + ".png",
            ).model_dump(exclude_unset=True)
        )
    )
    db.execute(stmt)
    db.commit()
    return JSONResponse(content={"message": "success"})




@router.get("/photo")
def get_photo(
    current_doctor: Annotated[Doctor, Depends(get_current_user)],
    request: Request,
    db: Session = Depends(get_db),
):
    """**Get the doctor's profile photo**"""
    stmt = select(Doctor).where(Doctor.id == current_doctor.id)
    portait_url = db.scalars(stmt).first().portrait
    url = get_url(request, 'get_photo')
    return RedirectResponse(
        url=url + "photos/" + portait_url,
        status_code=status.HTTP_302_FOUND,
    )