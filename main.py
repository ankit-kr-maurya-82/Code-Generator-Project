from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from routes.generate import router as generate_router
from routes.history import router as history_router
from db import init_db

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )

@app.on_event("startup")
def on_startup():
    # Ensure database tables exist
    init_db()

app.include_router(generate_router)
app.include_router(history_router)
