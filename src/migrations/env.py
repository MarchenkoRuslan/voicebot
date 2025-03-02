import os
import sys
from pathlib import Path
from sqlalchemy import engine_from_config
from sqlalchemy import pool

# Add parent directory to path to find src package
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.core.models import Base
from logging.config import fileConfig
from alembic import context

config = context.config

# Получаем компоненты URL из переменных окружения
pguser = os.getenv('PGUSER')
pgpass = os.getenv('PGPASSWORD')
pghost = os.getenv('PGHOST')
pgport = os.getenv('PGPORT')
pgdb = os.getenv('PGDATABASE')

if not all([pguser, pgpass, pghost, pgport, pgdb]):
    raise ValueError("Database configuration is incomplete")

# Формируем URL
db_url = f"postgresql://{pguser}:{pgpass}@{pghost}:{pgport}/{pgdb}"
print(f"Using database URL: {db_url}")  # Для отладки

# Устанавливаем URL для миграций
config.set_main_option('sqlalchemy.url', db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
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
