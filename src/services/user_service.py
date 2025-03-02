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

    async def create_user(self, telegram_id: int, thread_id: str = None,
                         username: str = None, first_name: str = None,
                         last_name: str = None) -> User:
        user = User(
            telegram_id=telegram_id,
            assistant_thread_id=thread_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        self.session.add(user)
        await self.session.commit()
        return user

    async def update_user_thread(self, user: User, thread_id: str) -> User:
        user.assistant_thread_id = thread_id
        await self.session.commit()
        return user

    async def update_user_values(self, user: User, value: str) -> None:
        if user.values is None:
            user.values = []
        user.values.append(value)
        await self.session.commit() 