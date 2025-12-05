"""
Тесты для операций с базой данных
"""
import pytest
from sqlalchemy import func, text
from models import Expense
from database import get_db


def test_database_connection(test_db):
    """Тест подключения к БД"""
    assert test_db is not None
    assert test_db.bind is not None


def test_database_table_creation(test_db):
    """Тест создания таблиц"""
    # Проверяем, что таблица expenses существует
    result = test_db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='expenses'"))
    table = result.fetchone()
    assert table is not None
    assert table[0] == "expenses"


def test_database_insert_and_retrieve(test_db):
    """Тест вставки и получения данных"""
    expense = Expense(
        date="2024-01-15",
        category="Еда",
        amount=500.0,
        comment="Тест"
    )
    
    test_db.add(expense)
    test_db.commit()
    
    retrieved = test_db.query(Expense).first()
    assert retrieved is not None
    assert retrieved.date == "2024-01-15"
    assert retrieved.category == "Еда"
    assert retrieved.amount == 500.0


def test_database_update(test_db):
    """Тест обновления данных"""
    expense = Expense(date="2024-01-15", category="Еда", amount=500.0)
    test_db.add(expense)
    test_db.commit()
    test_db.refresh(expense)
    
    expense.amount = 600.0
    expense.comment = "Обновлено"
    test_db.commit()
    
    updated = test_db.query(Expense).filter(Expense.id == expense.id).first()
    assert updated.amount == 600.0
    assert updated.comment == "Обновлено"


def test_database_delete(test_db):
    """Тест удаления данных"""
    expense = Expense(date="2024-01-15", category="Еда", amount=500.0)
    test_db.add(expense)
    test_db.commit()
    test_db.refresh(expense)
    
    expense_id = expense.id
    test_db.delete(expense)
    test_db.commit()
    
    deleted = test_db.query(Expense).filter(Expense.id == expense_id).first()
    assert deleted is None


def test_database_aggregations(test_db, sample_expenses):
    """Тест агрегирующих запросов"""
    # Общая сумма
    total = test_db.query(func.sum(Expense.amount)).scalar()
    assert total == 3600.0  # 500 + 200 + 800 + 1500 + 600
    
    # Средняя сумма
    avg = test_db.query(func.avg(Expense.amount)).scalar()
    assert avg == 720.0
    
    # Количество записей
    count = test_db.query(func.count(Expense.id)).scalar()
    assert count == 5


def test_database_group_by_category(test_db, sample_expenses):
    """Тест группировки по категориям"""
    results = test_db.query(
        Expense.category,
        func.sum(Expense.amount).label("total")
    ).group_by(Expense.category).all()
    
    category_totals = {r.category: r.total for r in results}
    
    assert category_totals["Еда"] == 1900.0  # 500 + 800 + 600
    assert category_totals["Транспорт"] == 200.0
    assert category_totals["Развлечения"] == 1500.0


def test_database_filter_by_date_prefix(test_db, sample_expenses):
    """Тест фильтрации по префиксу даты (месяц)"""
    jan_expenses = test_db.query(Expense).filter(
        Expense.date.like("2024-01%")
    ).all()
    
    assert len(jan_expenses) == 2


def test_database_order_by(test_db, sample_expenses):
    """Тест сортировки"""
    # Сортировка по дате
    by_date = test_db.query(Expense).order_by(Expense.date).all()
    assert by_date[0].date == "2024-01-15"
    assert by_date[-1].date == "2024-03-05"
    
    # Сортировка по сумме
    by_amount = test_db.query(Expense).order_by(Expense.amount.desc()).all()
    assert by_amount[0].amount == 1500.0
    assert by_amount[-1].amount == 200.0

