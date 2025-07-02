from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import UserORM
from app.schemas.user_schema import User


class UserRepository():
    def __init__(self, session: AsyncSession) -> UserORM:
        self.session = session

    async def create_user(self, user: User):
        result = await self.session.execute(
            select(UserORM).where(UserORM.telegram_id == user.telegram_id)
        )
        existing_user = result.scalars().first()
        if existing_user:
            return existing_user
        new_user = UserORM(
            telegram_id=user.telegram_id,
            username=user.username,
        )
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user
