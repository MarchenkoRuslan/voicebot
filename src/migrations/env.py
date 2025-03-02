import os
import sys
import psycopg2
from logging.config import fileConfig
from sqlalchemy import create_engine
from sqlalchemy import pool

# Add parent directory to path to find src package
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.core.models import Base
from alembic import context

config = context.config

# Получаем компоненты подключения
pguser = os.getenv('PGUSER')
pgpass = os.getenv('PGPASSWORD')
pghost = os.getenv('PGHOST')
pgport = os.getenv('PGPORT')
pgdb = os.getenv('PGDATABASE')

if not all([pguser, pgpass, pghost, pgport, pgdb]):
    raise ValueError("Database configuration is incomplete")

# Формируем DSN для psycopg2
dsn = f"dbname={pgdb} user={pguser} password={pgpass} host={pghost} port={pgport}"

# Пробуем подключиться напрямую через psycopg2
try:
    conn = psycopg2.connect(dsn)
    conn.close()
    print("Test connection successful")
except Exception as e:
    print(f"Test connection failed: {e}")
    raise

# Формируем URL для SQLAlchemy
database_url = f"postgresql://{pguser}:{pgpass}@{pghost}:{pgport}/{pgdb}"
print(f"Using database URL: {database_url}")

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
    connectable = create_engine(database_url)

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
