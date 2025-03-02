import os
import sys
from logging.config import fileConfig
from sqlalchemy import create_engine
from sqlalchemy import pool

# Add parent directory to path to find src package
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.core.models import Base
from alembic import context

config = context.config

# Получаем DATABASE_URL
database_url = os.getenv('DATABASE_URL')
if not database_url:
    raise ValueError("DATABASE_URL is not set")

# Заменяем postgres:// на postgresql://
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

# Убираем +asyncpg если есть
if '+asyncpg' in database_url:
    database_url = database_url.replace('+asyncpg', '')

print(f"Using database URL: {database_url}")  # Для отладки

# Устанавливаем URL
config.set_main_option('sqlalchemy.url', database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    # Создаем engine напрямую
    engine = create_engine(database_url, poolclass=pool.NullPool)

    with engine.connect() as connection:
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
