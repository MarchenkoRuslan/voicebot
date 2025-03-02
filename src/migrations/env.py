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

# Выводим все переменные окружения для отладки
print("Environment variables:")
for key, value in os.environ.items():
    if any(x in key.lower() for x in ['db', 'sql', 'pg', 'database']):
        # Скрываем пароль
        if 'pass' in key.lower():
            print(f"{key}=***")
        else:
            print(f"{key}={value}")

# Пробуем получить URL разными способами
database_url = os.getenv('DATABASE_URL')
if not database_url:
    # Пробуем собрать из компонентов
    pguser = os.getenv('PGUSER')
    pgpass = os.getenv('PGPASSWORD')
    pghost = os.getenv('PGHOST')
    pgport = os.getenv('PGPORT')
    pgdb = os.getenv('PGDATABASE')
    
    if all([pguser, pgpass, pghost, pgport, pgdb]):
        database_url = f"postgresql://{pguser}:{pgpass}@{pghost}:{pgport}/{pgdb}"
    else:
        print("Missing environment variables:")
        print(f"PGUSER: {'✓' if pguser else '✗'}")
        print(f"PGPASSWORD: {'✓' if pgpass else '✗'}")
        print(f"PGHOST: {'✓' if pghost else '✗'}")
        print(f"PGPORT: {'✓' if pgport else '✗'}")
        print(f"PGDATABASE: {'✓' if pgdb else '✗'}")
        raise ValueError("No database configuration available")

print(f"Final database URL: {database_url.replace(os.getenv('PGPASSWORD', ''), '***') if database_url else 'None'}")

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
