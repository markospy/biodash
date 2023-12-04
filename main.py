from contextlib import asynccontextmanager

from fastapi import FastAPI

from routes import user
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


app.include_router(user.router)


@app.get("/")
async def root():
    return {
        "message": "This aplication can be used to keep track of blood pressure values"
    }
