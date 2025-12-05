"""
Главный модуль FastAPI приложения для учета расходов
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from database import init_db
from config import TEMPLATES_DIR
from routers import upload, reports

# === Инициализация приложения ===
app = FastAPI(
    title="Expense Tracker",
    description="Приложение для учета расходов с генерацией отчетов",
    version="2.0.0"
)

# Инициализация шаблонов
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Инициализация базы данных
init_db()

# === Подключение роутеров ===
app.include_router(upload.router, tags=["Upload"])
app.include_router(reports.router, tags=["Reports"])


# === Главная страница ===
@app.get("/", response_class=HTMLResponse, tags=["Main"])
async def index(request: Request):
    """Главная страница приложения"""
    return templates.TemplateResponse("index.html", {"request": request})


# === Документация ===
@app.get("/docs-page", response_class=HTMLResponse, tags=["Main"])
async def docs_page(request: Request):
    """Страница с документацией по API"""
    return templates.TemplateResponse("docs.html", {"request": request})
