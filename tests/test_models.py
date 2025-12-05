"""
Тесты для моделей базы данных
"""
import pytest
from models import Expense


def test_expense_creation(test_db):
    """Тест создания модели Expense"""
    expense = Expense(
        date="2024-01-15",
        category="Еда",
        amount=500.0,
        comment="Тестовый комментарий"
    )
    
    test_db.add(expense)
    test_db.commit()
    test_db.refresh(expense)
    
    assert expense.id is not None
    assert expense.date == "2024-01-15"
    assert expense.category == "Еда"
    assert expense.amount == 500.0
    assert expense.comment == "Тестовый комментарий"


def test_expense_without_comment(test_db):
    """Тест создания Expense без комментария"""
    expense = Expense(
        date="2024-02-20",
        category="Транспорт",
        amount=150.0
    )
    
    test_db.add(expense)
    test_db.commit()
    test_db.refresh(expense)
    
    assert expense.id is not None
    assert expense.comment is None


def test_expense_repr(test_db):
    """Тест строкового представления модели"""
    expense = Expense(
        date="2024-03-10",
        category="Еда",
        amount=300.0
    )
    
    test_db.add(expense)
    test_db.commit()
    test_db.refresh(expense)
    
    repr_str = repr(expense)
    assert "Expense" in repr_str
    assert "2024-03-10" in repr_str
    assert "Еда" in repr_str
    assert "300.0" in repr_str


def test_multiple_expenses(test_db):
    """Тест создания нескольких расходов"""
    expenses = [
        Expense(date="2024-01-01", category="Еда", amount=100.0),
        Expense(date="2024-01-02", category="Транспорт", amount=200.0),
        Expense(date="2024-01-03", category="Развлечения", amount=300.0),
    ]
    
    for expense in expenses:
        test_db.add(expense)
    test_db.commit()
    
    all_expenses = test_db.query(Expense).all()
    assert len(all_expenses) == 3


def test_expense_query_by_category(test_db):
    """Тест запроса расходов по категории"""
    test_db.add(Expense(date="2024-01-01", category="Еда", amount=100.0))
    test_db.add(Expense(date="2024-01-02", category="Еда", amount=200.0))
    test_db.add(Expense(date="2024-01-03", category="Транспорт", amount=300.0))
    test_db.commit()
    
    food_expenses = test_db.query(Expense).filter(Expense.category == "Еда").all()
    assert len(food_expenses) == 2
    assert all(e.category == "Еда" for e in food_expenses)


def test_expense_query_by_amount_range(test_db):
    """Тест запроса расходов по диапазону сумм"""
    test_db.add(Expense(date="2024-01-01", category="Еда", amount=100.0))
    test_db.add(Expense(date="2024-01-02", category="Транспорт", amount=500.0))
    test_db.add(Expense(date="2024-01-03", category="Развлечения", amount=1000.0))
    test_db.commit()
    
    mid_range_expenses = test_db.query(Expense).filter(
        Expense.amount >= 200.0,
        Expense.amount <= 800.0
    ).all()
    
    assert len(mid_range_expenses) == 1
    assert mid_range_expenses[0].amount == 500.0

