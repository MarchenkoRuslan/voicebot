from typing import Optional
from datetime import datetime
from sqlalchemy import BigInteger, String, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    assistant_thread_id: Mapped[Optional[str]] = mapped_column(String)
    values: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=text('CURRENT_TIMESTAMP'),
        nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        server_default=text('CURRENT_TIMESTAMP'),
        server_onupdate=text('CURRENT_TIMESTAMP'),
        nullable=True
    ) 