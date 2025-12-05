"""
Тесты для главного модуля приложения
"""
import pytest
from fastapi import status


def test_main_page(client):
    """Тест главной страницы"""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]


def test_docs_page(client):
    """Тест страницы документации"""
    response = client.get("/docs-page")
    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]


def test_openapi_schema(client):
    """Тест доступности OpenAPI схемы"""
    response = client.get("/openapi.json")
    assert response.status_code == status.HTTP_200_OK
    
    schema = response.json()
    assert schema["info"]["title"] == "Expense Tracker"
    assert schema["info"]["version"] == "2.0.0"


def test_swagger_docs(client):
    """Тест доступности Swagger документации"""
    response = client.get("/docs")
    assert response.status_code == status.HTTP_200_OK


def test_redoc_docs(client):
    """Тест доступности ReDoc документации"""
    response = client.get("/redoc")
    assert response.status_code == status.HTTP_200_OK


def test_invalid_route(client):
    """Тест несуществующего маршрута"""
    response = client.get("/nonexistent")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_app_metadata():
    """Тест метаданных приложения"""
    from main import app
    
    assert app.title == "Expense Tracker"
    assert app.description == "Приложение для учета расходов с генерацией отчетов"
    assert app.version == "2.0.0"


def test_routers_included():
    """Тест подключения роутеров"""
    from main import app
    
    # Получаем все маршруты
    routes = [route.path for route in app.routes]
    
    # Проверяем наличие основных маршрутов
    assert "/upload" in routes
    assert "/report" in routes
    assert "/report/pdf" in routes

