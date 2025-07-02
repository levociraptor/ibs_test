from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.orm import selectinload

from app.models import ChatORM
from app.models import UserORM
from app.models import Status


class ChatRepository():
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_admin_chats(self, admin_id: int) -> list[ChatORM]:
        query = (
            select(ChatORM)
            .where(
                ChatORM.admin_id == admin_id,
                ChatORM.status == Status.PENDING,
            )
            .options(
                selectinload(ChatORM.user),
                selectinload(ChatORM.messages),
            )
            .order_by(ChatORM.created_at)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_chat(self, chat_id: int) -> ChatORM:
        result = await self.session.execute(
            select(ChatORM)
            .options(selectinload(ChatORM.user))
            .where(ChatORM.id == chat_id)
        )
        return result.scalar_one_or_none()

    async def create_room(self, user: UserORM) -> ChatORM:
        result = await self.session.execute(
            select(ChatORM).where(ChatORM.user_id == user.id)
        )
        existing_chat = result.scalars().first()
        if existing_chat:
            existing_chat.status = Status.NEW
            await self.session.commit()
            return existing_chat
        new_chat = ChatORM(
            user_id=user.id,
        )
        self.session.add(new_chat)
        await self.session.commit()
        await self.session.refresh(new_chat)
        return new_chat

    async def assign_chat(self, admin_id: int, chat: ChatORM) -> None:
        chat.admin_id = admin_id
        chat.status = Status.PENDING
        self.session.add(chat)
        await self.session.commit()

    async def update_chat_status(self, chat_id: int, status: str):
        stmt = update(ChatORM).where(ChatORM.id == chat_id).values(status=status)
        await self.session.execute(stmt)
        await self.session.commit()
