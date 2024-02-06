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


app = FastAPI(
    lifespan=lifespan,
    summary="Main features:  1.Jwt-oauth registration and login system  2.Account verification by email.  3.Complex relational database queries",
    description="This Rest API facilitates the control of patients' vital parameters (blood pressure, heart rate and blood glucose). It allows a doctor to create an account and register their patients to keep track of the mentioned parameters.",
)


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
