from contextlib import asynccontextmanager

from fastapi import FastAPI

from routes import (
    analize_blood_pressure,
    analize_blood_sugar,
    blood_pressure,
    blood_sugar,
    doctors,
    jwt_oauth_doctor,
    patients,
    email,
)
from models.models import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        create_tables()
        yield
    except Exception as e:
        # Handle the exception or log the error
        print(f"Error occurred during database initialization: {e}")


app = FastAPI(lifespan=lifespan)


app.include_router(doctors.router)
app.include_router(patients.router)
app.include_router(blood_pressure.router)
app.include_router(blood_sugar.router)
app.include_router(analize_blood_pressure.router)
app.include_router(analize_blood_sugar.router)
app.include_router(email.router)
app.include_router(jwt_oauth_doctor.router)


@app.get("/")
async def root():
    return {
        "message": "This aplication can be used to keep track of blood pressure values"
    }
