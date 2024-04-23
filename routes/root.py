from jinja2 import Environment, FileSystemLoader
from fastapi.responses import HTMLResponse
from fastapi import APIRouter


# Carga la plantilla
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("root.html")

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def root():
    return template.render()