from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.models import User

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, telegram_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def create_user(self, telegram_id: int, thread_id: str) -> User:
        user = User(
            telegram_id=telegram_id,
            assistant_thread_id=thread_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_user_thread(self, user: User, thread_id: str) -> User:
        user.assistant_thread_id = thread_id
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_user_values(self, user: User, values: str) -> User:
        user.values = values
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user 