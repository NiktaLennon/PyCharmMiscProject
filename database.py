"""
Настройка базы данных и сессий SQLAlchemy
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DB_PATH

# Создание engine
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})

# Фабрика сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


def get_db():
    """
    Dependency для получения сессии БД.
    Автоматически закрывает соединение после использования.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Создание всех таблиц в БД"""
    from models import Expense  # импорт здесь для избежания циклических зависимостей
    Base.metadata.create_all(bind=engine)

