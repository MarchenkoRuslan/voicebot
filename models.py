from sqlalchemy import Column, Integer, String, BigInteger, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)
    assistant_thread_id = Column(String)
    # Используем server_default для установки значения на уровне базы данных
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    values: Mapped[Optional[str]]
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow) 