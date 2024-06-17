from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routes import root

from routes.doctor_scope import (
    analize_blood_pressure,
    analize_blood_sugar,
    blood_pressure,
    blood_sugar,
    doctors,
    patients,
    email,
    photo,
)
from routes import oauth
from routes.patient_scope import (
    analize_blood_pressure_patient,
    analize_blood_sugar_patient,
    blood_pressure_patient,
    blood_sugar_patient,
    patient,
)
from database.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        create_tables()
        yield
    except Exception as e:
        # Handle the exception or log the error
        print(f"Error occurred during database initialization: {e}")


app = FastAPI(
    title="BioDash",
    lifespan=lifespan,
    description="This Rest API facilitates the control of patients' vital parameters (blood pressure, heart rate and blood glucose). It allows a doctor to create an account and register their patients to keep track of the mentioned parameters.",
)

app.mount("/photos", StaticFiles(directory="photos"), name="photos")

app.include_router(root.router)
app.include_router(doctors.router)
app.include_router(patients.router)
app.include_router(blood_pressure.router)
app.include_router(blood_sugar.router)
app.include_router(analize_blood_pressure.router)
app.include_router(analize_blood_sugar.router)
app.include_router(email.router)
app.include_router(photo.router)
app.include_router(oauth.router)
app.include_router(patient.router)
app.include_router(blood_pressure_patient.router)
app.include_router(blood_sugar_patient.router)
app.include_router(analize_blood_pressure_patient.router)
app.include_router(analize_blood_sugar_patient.router)
