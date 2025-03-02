import os
import sys
from logging.config import fileConfig
from sqlalchemy import create_engine
from sqlalchemy import pool
from urllib.parse import urlparse

# Add parent directory to path to find src package
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.core.models import Base
from alembic import context

config = context.config

# Получаем DATABASE_URL
database_url = os.getenv('DATABASE_URL')
if not database_url:
    raise ValueError("DATABASE_URL is not set")

# Парсим URL для получения компонентов
parsed = urlparse(database_url)
if parsed.scheme == 'postgres':
    scheme = 'postgresql'
else:
    scheme = parsed.scheme.replace('+asyncpg', '')

# Получаем хост из PGHOST если он есть
pghost = os.getenv('PGHOST')
if pghost:
    host = pghost
else:
    host = parsed.hostname

# Формируем новый URL
new_url = f"{scheme}://{parsed.username}:{parsed.password}@{host}:{parsed.port}{parsed.path}"

print(f"Original URL: {database_url}")  # Для отладки
print(f"New URL: {new_url}")  # Для отладки

# Устанавливаем URL
config.set_main_option('sqlalchemy.url', new_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    context.configure(
        url=new_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    # Создаем engine с новым URL
    engine = create_engine(new_url, poolclass=pool.NullPool)

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
