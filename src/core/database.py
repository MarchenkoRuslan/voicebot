from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.core.config import settings

engine = create_async_engine(
    settings.get_database_url,
    echo=True,
    pool_size=5,
    max_overflow=10
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def test_connection():
    try:
        async with async_session() as session:
            await session.execute("SELECT 1")
            print("Database connection successful!")
    except Exception as e:
        print(f"Database connection failed: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_connection()) 