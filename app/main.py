from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.routers import user, task, auth
from app.database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Инициализация при старте
    await init_db()
    yield
    # Очистка при остановке
    await close_db()


app = FastAPI(lifespan=lifespan)

# Указываем папку с шаблонами
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Роутеры (префиксы уже указаны в роутерах)
app.include_router(user.router)
app.include_router(task.router)
app.include_router(auth.router)


# Стартовая страница
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
