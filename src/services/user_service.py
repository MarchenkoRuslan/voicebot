from typing import Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.models import User

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, telegram_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def create_user(self, telegram_id: int, username: str = None,
                         first_name: str = None, last_name: str = None) -> User:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        self.session.add(user)
        await self.session.commit()
        return user

    async def update_thread_id(self, telegram_id: int, thread_id: str) -> None:
        user = await self.get_user(telegram_id)
        if user:
            user.assistant_thread_id = thread_id
            await self.session.commit()

    async def update_user_values(self, user: User, values: str) -> User:
        user.values = values
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user 