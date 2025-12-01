from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.routers import user, task, auth
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Указываем папку с шаблонами
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Роутер
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(task.router, prefix="/tasks", tags=["Tasks"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])


# Стартовая страница
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
