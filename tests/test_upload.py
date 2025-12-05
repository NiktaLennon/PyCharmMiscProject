"""
Тесты для роутера загрузки файлов
"""
import pytest
from io import BytesIO
from fastapi import status
from models import Expense


def test_upload_page_get(client):
    """Тест GET запроса на страницу загрузки"""
    response = client.get("/upload")
    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]


def test_upload_valid_file(client, test_db):
    """Тест загрузки корректного файла"""
    file_content = """2024-01-15;Еда;500.0;Продукты
2024-01-20;Транспорт;200.0;Метро
2024-02-10;Развлечения;1500.0;Кино""".encode("utf-8")
    
    files = {"file": ("expenses.txt", BytesIO(file_content), "text/plain")}
    response = client.post("/upload", files=files)
    
    assert response.status_code == status.HTTP_200_OK
    
    # Проверяем, что записи добавлены в БД
    expenses = test_db.query(Expense).all()
    assert len(expenses) == 3
    assert expenses[0].category == "Еда"
    assert expenses[0].amount == 500.0


def test_upload_file_without_comment(client, test_db):
    """Тест загрузки файла без комментариев"""
    file_content = """2024-01-15;Еда;500.0
2024-01-20;Транспорт;200.0""".encode("utf-8")
    
    files = {"file": ("expenses.txt", BytesIO(file_content), "text/plain")}
    response = client.post("/upload", files=files)
    
    assert response.status_code == status.HTTP_200_OK
    
    expenses = test_db.query(Expense).all()
    assert len(expenses) == 2
    assert expenses[0].comment is None


def test_upload_file_with_alternative_date_format(client, test_db):
    """Тест загрузки файла с альтернативным форматом даты (dd.mm.yyyy)"""
    file_content = """15.01.2024;Еда;500.0;Продукты
20.01.2024;Транспорт;200.0;Метро""".encode("utf-8")
    
    files = {"file": ("expenses.txt", BytesIO(file_content), "text/plain")}
    response = client.post("/upload", files=files)
    
    assert response.status_code == status.HTTP_200_OK
    
    expenses = test_db.query(Expense).all()
    assert len(expenses) == 2


def test_upload_file_with_invalid_date(client, test_db):
    """Тест загрузки файла с некорректной датой"""
    file_content = """invalid-date;Еда;500.0;Продукты
2024-01-20;Транспорт;200.0;Метро""".encode("utf-8")
    
    files = {"file": ("expenses.txt", BytesIO(file_content), "text/plain")}
    response = client.post("/upload", files=files)
    
    assert response.status_code == status.HTTP_200_OK
    
    # Должна быть добавлена только одна корректная запись
    expenses = test_db.query(Expense).all()
    assert len(expenses) == 1
    assert expenses[0].category == "Транспорт"


def test_upload_file_with_negative_amount(client, test_db):
    """Тест загрузки файла с отрицательной суммой"""
    file_content = """2024-01-15;Еда;-500.0;Продукты
2024-01-20;Транспорт;200.0;Метро""".encode("utf-8")
    
    files = {"file": ("expenses.txt", BytesIO(file_content), "text/plain")}
    response = client.post("/upload", files=files)
    
    assert response.status_code == status.HTTP_200_OK
    
    # Должна быть добавлена только запись с положительной суммой
    expenses = test_db.query(Expense).all()
    assert len(expenses) == 1
    assert expenses[0].amount == 200.0


def test_upload_file_with_zero_amount(client, test_db):
    """Тест загрузки файла с нулевой суммой"""
    file_content = """2024-01-15;Еда;0;Продукты
2024-01-20;Транспорт;200.0;Метро""".encode("utf-8")
    
    files = {"file": ("expenses.txt", BytesIO(file_content), "text/plain")}
    response = client.post("/upload", files=files)
    
    assert response.status_code == status.HTTP_200_OK
    
    # Нулевая сумма должна быть отклонена
    expenses = test_db.query(Expense).all()
    assert len(expenses) == 1


def test_upload_file_with_invalid_amount(client, test_db):
    """Тест загрузки файла с некорректной суммой"""
    file_content = """2024-01-15;Еда;not-a-number;Продукты
2024-01-20;Транспорт;200.0;Метро""".encode("utf-8")
    
    files = {"file": ("expenses.txt", BytesIO(file_content), "text/plain")}
    response = client.post("/upload", files=files)
    
    assert response.status_code == status.HTTP_200_OK
    
    expenses = test_db.query(Expense).all()
    assert len(expenses) == 1


def test_upload_file_with_insufficient_fields(client, test_db):
    """Тест загрузки файла с недостаточным количеством полей"""
    file_content = """2024-01-15;Еда
2024-01-20;Транспорт;200.0;Метро""".encode("utf-8")
    
    files = {"file": ("expenses.txt", BytesIO(file_content), "text/plain")}
    response = client.post("/upload", files=files)
    
    assert response.status_code == status.HTTP_200_OK
    
    # Должна быть добавлена только корректная запись
    expenses = test_db.query(Expense).all()
    assert len(expenses) == 1


def test_upload_file_with_empty_lines(client, test_db):
    """Тест загрузки файла с пустыми строками"""
    file_content = """2024-01-15;Еда;500.0;Продукты

2024-01-20;Транспорт;200.0;Метро

""".encode("utf-8")
    
    files = {"file": ("expenses.txt", BytesIO(file_content), "text/plain")}
    response = client.post("/upload", files=files)
    
    assert response.status_code == status.HTTP_200_OK
    
    # Пустые строки должны быть проигнорированы
    expenses = test_db.query(Expense).all()
    assert len(expenses) == 2


def test_upload_empty_file(client, test_db):
    """Тест загрузки пустого файла"""
    file_content = b""
    
    files = {"file": ("expenses.txt", BytesIO(file_content), "text/plain")}
    response = client.post("/upload", files=files)
    
    assert response.status_code == status.HTTP_200_OK
    
    expenses = test_db.query(Expense).all()
    assert len(expenses) == 0


def test_upload_file_with_mixed_valid_invalid(client, test_db):
    """Тест загрузки файла со смешанными корректными и некорректными данными"""
    file_content = """2024-01-15;Еда;500.0;Продукты
invalid-date;Транспорт;200.0;Метро
2024-02-10;Развлечения;-100.0;Кино
2024-03-05;Еда;300.0;Кафе
2024-03-10;Транспорт;abc;Такси""".encode("utf-8")
    
    files = {"file": ("expenses.txt", BytesIO(file_content), "text/plain")}
    response = client.post("/upload", files=files)
    
    assert response.status_code == status.HTTP_200_OK
    
    # Должны быть добавлены только две корректные записи
    expenses = test_db.query(Expense).all()
    assert len(expenses) == 2
    assert expenses[0].amount == 500.0
    assert expenses[1].amount == 300.0

