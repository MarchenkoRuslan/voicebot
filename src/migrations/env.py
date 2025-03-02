import os
import sys
from pathlib import Path
from sqlalchemy import engine_from_config
from sqlalchemy import pool

# Add parent directory to path to find src package
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.core.models import Base
from src.core.config import settings
from logging.config import fileConfig
from alembic import context

config = context.config

# Получаем URL и заменяем драйвер
db_url = settings.get_database_url.replace("+asyncpg", "")

# Для отладки
print(f"Using database URL: {db_url}")

# Создаем новую секцию конфигурации
ini_section = config.get_section(config.config_ini_section) or {}
ini_section["sqlalchemy.url"] = db_url

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = db_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    # Используем только DATABASE_URL из Railway
    configuration = {
        "sqlalchemy.url": settings.DATABASE_URL.replace("+asyncpg", "") if settings.DATABASE_URL else db_url
    }
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
