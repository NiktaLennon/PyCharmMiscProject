"""
Модели базы данных
"""
from sqlalchemy import Column, Integer, String, Float
from database import Base


class Expense(Base):
    """Модель расхода"""
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=False)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    comment = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<Expense(id={self.id}, date={self.date}, category={self.category}, amount={self.amount})>"

