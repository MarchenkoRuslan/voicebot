import os
import sys
from logging.config import fileConfig
from sqlalchemy import create_engine
from sqlalchemy import pool
from dotenv import load_dotenv

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

# Пробуем получить DATABASE_URL или собрать из компонентов
database_url = os.getenv('DATABASE_URL')
if not database_url:
    # Получаем компоненты
    pguser = os.getenv('PGUSER')
    pgpass = os.getenv('PGPASSWORD')
    pghost = os.getenv('PGHOST')
    pgport = os.getenv('PGPORT')
    pgdb = os.getenv('PGDATABASE')
    
    if all([pguser, pgpass, pghost, pgport, pgdb]):
        database_url = f"postgresql://{pguser}:{pgpass}@{pghost}:{pgport}/{pgdb}"
    else:
        raise ValueError("Neither DATABASE_URL nor individual PG* variables are set")

print(f"Original URL: {database_url}")

# Проверяем, не используем ли мы Railway internal hostname
if '.railway.internal' in database_url:
    # Парсим существующий URL для получения креденшелов
    from urllib.parse import urlparse
    parsed = urlparse(database_url)
    username = parsed.username
    password = parsed.password
    dbname = parsed.path.lstrip('/')
    
    # Создаем новый URL с публичным хостом Railway
    database_url = f"postgresql://{username}:{password}@interchange.proxy.rlwy.net:31830/{dbname}"

print(f"Using URL: {database_url.replace(os.getenv('PGPASSWORD', ''), '***')}")

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
    engine = create_engine(
        database_url,
        poolclass=pool.NullPool,
        connect_args={
            'connect_timeout': 60,
            'keepalives': 1,
            'keepalives_idle': 30
        }
    )

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
