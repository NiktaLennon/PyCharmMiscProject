"""
Роутер для загрузки файлов с расходами
"""
from fastapi import APIRouter, Request, UploadFile, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime as dt

from database import get_db
from models import Expense
from config import TEMPLATES_DIR

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    """Страница загрузки файла"""
    return templates.TemplateResponse("upload.html", {"request": request})


@router.post("/upload", response_class=HTMLResponse)
async def upload_file(request: Request, file: UploadFile, db: Session = Depends(get_db)):
    """Обработка загруженного файла с расходами"""
    inserted, errors = 0, []

    content = await file.read()
    lines = content.decode("utf-8").splitlines()

    for line in lines:
        try:
            line = line.strip()
            if not line:
                continue
            parts = line.split(";")
            if len(parts) < 3:
                errors.append(f"Недостаточно полей: {line}")
                continue

            # Валидация даты
            try:
                try:
                    dt.strptime(parts[0], "%Y-%m-%d")
                except ValueError:
                    dt.strptime(parts[0], "%d.%m.%Y")
            except Exception:
                errors.append(f"Неверная дата: {line}")
                continue

            # Валидация суммы
            try:
                amount = float(parts[2])
                if amount <= 0:
                    raise ValueError
            except Exception:
                errors.append(f"Неверная сумма: {line}")
                continue

            # Создание записи в БД
            expense = Expense(
                date=parts[0],
                category=parts[1],
                amount=amount,
                comment=parts[3] if len(parts) > 3 else None
            )
            db.add(expense)
            inserted += 1

        except Exception as e:
            errors.append(str(e))

    db.commit()

    return templates.TemplateResponse("upload.html", {
        "request": request,
        "inserted": inserted,
        "errors": errors,
    })

