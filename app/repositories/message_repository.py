from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.chat_schema import ChatSchema
from app.models import MessageORM


class MessageRepository():
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_message(
        self,
        chat_id: int,
        text: str,
        user_id: int,
        message_type: str,
    ) -> list[ChatSchema]:
        message = MessageORM(
            chat_id=chat_id,
            type_message=message_type,
            sender_id=user_id,
            content=text,
        )
        self.session.add(message)
        await self.session.commit()
