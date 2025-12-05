"""
Роутер для генерации отчетов (HTML и PDF)
"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime as dt
import pdfkit

from database import get_db
from models import Expense
from config import TEMPLATES_DIR, PDF_PATH, WKHTMLTOPDF_PATH

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/report", response_class=HTMLResponse)
async def report_page(request: Request, db: Session = Depends(get_db)):
    """HTML-отчет со статистикой расходов"""
    # Общие статистики
    stats = db.query(
        func.sum(Expense.amount).label("total"),
        func.avg(Expense.amount).label("avg")
    ).first()
    total = stats.total or 0
    avg = stats.avg or 0

    # Статистика по месяцам
    by_month = db.query(
        func.substr(Expense.date, 1, 7).label("month"),
        func.sum(Expense.amount).label("sum"),
        func.avg(Expense.amount).label("avg")
    ).group_by(func.substr(Expense.date, 1, 7)).order_by("month").all()

    # Статистика по категориям
    by_category = db.query(
        Expense.category,
        func.sum(Expense.amount).label("sum"),
        func.avg(Expense.amount).label("avg")
    ).group_by(Expense.category).order_by(Expense.category).all()

    # Статистика по месяцам и категориям
    by_month_category = db.query(
        func.substr(Expense.date, 1, 7).label("month"),
        Expense.category,
        func.sum(Expense.amount).label("sum"),
        func.avg(Expense.amount).label("avg")
    ).group_by(
        func.substr(Expense.date, 1, 7),
        Expense.category
    ).order_by("month", Expense.category).all()

    return templates.TemplateResponse("report.html", {
        "request": request,
        "total": total,
        "avg": avg,
        "by_month": by_month,
        "by_category": by_category,
        "by_month_category": by_month_category,
    })


@router.get("/report/pdf")
async def report_pdf(db: Session = Depends(get_db)):
    """Генерация PDF-отчета"""
    # Общие статистики
    stats = db.query(
        func.sum(Expense.amount).label("total"),
        func.avg(Expense.amount).label("avg")
    ).first()
    total = stats.total or 0
    avg = stats.avg or 0

    # Статистика по месяцам
    by_month = db.query(
        func.substr(Expense.date, 1, 7).label("month"),
        func.sum(Expense.amount).label("sum"),
        func.avg(Expense.amount).label("avg")
    ).group_by(func.substr(Expense.date, 1, 7)).order_by("month").all()

    # Статистика по категориям
    by_category = db.query(
        Expense.category,
        func.sum(Expense.amount).label("sum"),
        func.avg(Expense.amount).label("avg")
    ).group_by(Expense.category).order_by(Expense.category).all()

    # Рендеринг HTML-шаблона
    template = templates.env.get_template("report.html.j2")
    html = template.render(
        total=total,
        avg=avg,
        month_stats=by_month,
        category_stats=by_category,
        generated_at=dt.now().strftime("%d.%m.%Y %H:%M"),
        current_year=dt.now().year,
    )

    # Генерация PDF
    config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
    pdfkit.from_string(html, PDF_PATH, configuration=config)

    return FileResponse(PDF_PATH, filename="report.pdf")

