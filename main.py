from fastapi import FastAPI
from routes import registration_form


app = FastAPI()

app.include_router(registration_form.router, prefix="/register")


@app.get("/")
async def root():
    return {
        "message": "This aplication can be used to keep track of blood pressure values"
    }
