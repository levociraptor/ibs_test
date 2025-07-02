from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.chat_repository import ChatRepository
from app.repositories.message_repository import MessageRepository
from app.models import Status
from app.models import ChatORM
from app.models import UserORM
from app.services.connection_service import manager


class ChatService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.chat_repository = ChatRepository(session)
        self.message_repository = MessageRepository(session)

    async def get_admin_chats(self, admin_id: int) -> list[ChatORM]:
        chats = await self.chat_repository.get_admin_chats(admin_id)
        chats_to_return = []
        for chat in chats:
            user_message = next(
                (msg.content for msg in chat.messages if msg.type_message == 'user'),
                "Сообщение пользователя не найдено"
            )
            llm_response = next(
                (msg.content for msg in chat.messages if msg.type_message == 'llm'),
                "Ответ LLM не найден"
            )
            chats_to_return.append({
                "chat_id": chat.id,
                "user_name": chat.user.username,
                "user_message": user_message,
                "llm_response": llm_response,
                "created_at": chat.created_at.isoformat(),
            })
        return chats_to_return

    async def assign_admin_to_chat(
            self,
            text: str,
            llm_response: str,
            chat: ChatORM,
            user: UserORM,
            admin_id: int,
    ):
        await self.chat_repository.assign_chat(admin_id, chat)
        await self.message_repository.save_message(
            chat.id,
            text,
            chat.user_id,
            "user",
        )
        await self.message_repository.save_message(
            chat.id,
            llm_response,
            chat.user_id,
            "llm",
        )
        new_message = {
            "type": "new_moderation_task",
            "task": {
                "chat_id": chat.id,
                "user_name": user.username,
                "user_message": text,
                "llm_response": llm_response,
                "created_at": chat.created_at.isoformat(),
            }
        }
        await manager.send_json(new_message, admin_id)
        print(f"✅ Чат {chat.id} назначен администратору {admin_id}")
        return admin_id

    async def send_message(self, admin_id: int, chat_id: int, content: str):
        from app.app import bot

        await self.chat_repository.update_chat_status(chat_id, Status.DONE)
        chat = await self.chat_repository.get_chat(chat_id)
        try:
            user_telegram_id = chat.user.telegram_id
            await bot.send_message(
                chat_id=user_telegram_id,
                text=content
            )
            print(f"Sent approved message to user {user_telegram_id} for chat {chat_id}")
        except Exception as e:
            print(f"Failed to send message to Telegram user {chat.user.telegram_id}. Error: {e}")
            return
