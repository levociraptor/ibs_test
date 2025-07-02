import random

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.chat_repository import ChatRepository
from app.repositories.user_reposotory import UserRepository
from app.services.chat_service import ChatService
from app.schemas.user_schema import User
from app.routers.websocket_router import manager
from app.exceptions import NoActiveAdmin
from app.config import settings

import ollama


class BotService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.chat_repository = ChatRepository(session)
        self.user_reposirory = UserRepository(session)
        self.chat_service = ChatService(session)

        self.ollama_client = ollama.Client(host=settings.OLLAMA_HOST)
        self.system_prompt = """
        Ты - администратор телеграмм чата и должен отвечать именно от имени от администратора.
        Важные правила:
        1. Никогда не используй теги <think> в ответах
        2. Не рассуждай вслух
        3. Отвечай вежливо и по делу. Если не знаешь ответа - так и скажи.
        4. Твои ответы должны быть на русском языке и не превышать 3-5 предложений.
        """

    async def _get_llm_response(self, text: str) -> str:
        messages = [
            {'role': 'system', 'content': self.system_prompt},
            {'role': 'user', 'content': text},
        ]

        try:
            response = self.ollama_client.chat(
                model="deepseek-r1",
                messages=messages,
                options={
                    'temperature': 0.7,
                    'num_predict': 500,
                    'raw': True,
                }
            )
            return response['message']['content']
        except Exception as e:
            return f"⚠️ Ошибка: {str(e)}"

    async def message_procces(self, user: User, text: str):
        user = await self.user_reposirory.create_user(user)
        chat = await self.chat_repository.create_room(user)
        active_admin_ids = list(manager.active_connections.keys())
        if not active_admin_ids:
            raise NoActiveAdmin
        admin_id = random.choice(active_admin_ids)
        llm_response = await self._get_llm_response(text)
        await self.chat_service.assign_admin_to_chat(text, llm_response, chat, user, admin_id)
