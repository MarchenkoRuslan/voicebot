import os
import sys
from logging.config import fileConfig
from sqlalchemy import create_engine
from sqlalchemy import pool
from urllib.parse import urlparse, urlunparse

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

# Получаем DATABASE_URL
database_url = os.getenv('DATABASE_URL')
if not database_url:
    raise ValueError("DATABASE_URL is not set")

print(f"Original URL: {database_url}")

# Парсим URL
parsed = urlparse(database_url)

# Заменяем internal hostname на публичный хост
if '.railway.internal' in parsed.hostname:
    # Получаем публичный хост из PGHOST
    pghost = os.getenv('PGHOST')
    if not pghost:
        raise ValueError("PGHOST is not set")
        
    # Создаем новый URL с публичным хостом
    new_url = urlunparse((
        'postgresql',  # scheme
        f"{parsed.username}:{parsed.password}@{pghost}:{parsed.port}",  # netloc
        parsed.path,  # path
        parsed.params,  # params
        parsed.query,  # query
        parsed.fragment  # fragment
    ))
    
    database_url = new_url

print(f"Using URL: {database_url.replace(parsed.password, '***')}")

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
