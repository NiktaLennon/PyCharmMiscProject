"""
Конфигурация тестов и фикстуры pytest
"""
import pytest
import os
import sys
import time
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Base, get_db
from models import Expense
from main import app


@pytest.fixture(scope="function")
def test_db():
    """Создает временную тестовую БД для каждого теста"""
    # Создаем временный файл для БД
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    database_url = f"sqlite:///{db_path}"
    
    # Создаем engine и сессию
    engine = create_engine(
        database_url, 
        connect_args={"check_same_thread": False},
        poolclass=None  # Отключаем пулинг для тестов
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    
    # Создаем сессию
    db = TestingSessionLocal()
    
    yield db
    
    # Очищаем после теста
    db.close()
    engine.dispose()  # Важно! Закрываем все соединения engine
    os.close(db_fd)
    
    # Пытаемся удалить файл с несколькими попытками (для Windows)
    for _ in range(5):
        try:
            os.unlink(db_path)
            break
        except PermissionError:
            time.sleep(0.1)


@pytest.fixture(scope="function")
def client(test_db):
    """Создает тестовый клиент FastAPI с тестовой БД"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_expenses(test_db):
    """Создает тестовые данные о расходах"""
    expenses = [
        Expense(date="2024-01-15", category="Еда", amount=500.0, comment="Продукты"),
        Expense(date="2024-01-20", category="Транспорт", amount=200.0, comment="Метро"),
        Expense(date="2024-02-10", category="Еда", amount=800.0, comment="Ресторан"),
        Expense(date="2024-02-15", category="Развлечения", amount=1500.0, comment="Кино"),
        Expense(date="2024-03-05", category="Еда", amount=600.0, comment=None),
    ]
    
    for expense in expenses:
        test_db.add(expense)
    test_db.commit()
    
    # Обновляем объекты
    for expense in expenses:
        test_db.refresh(expense)
    
    return expenses

