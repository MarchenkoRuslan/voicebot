from datetime import datetime
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    assistant_thread_id = Column(String, nullable=True)
    values = Column(JSON, nullable=True)  # Для хранения ценностей пользователя
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 