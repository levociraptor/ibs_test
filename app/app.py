import asyncio
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
from app.config import settings
from app.exceptions import NoActiveAdmin
from app.services.bot_service import BotService
from app.schemas.user_schema import User
from app.database import get_session
from app.routers.admin_router import router as admin_router
from app.routers.page_router import router as page_router
from app.routers.chat_router import router as chat_router
from app.routers.websocket_router import router as websocket_router


TOKEN = settings.TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

bot_data = {"is_running": False}


@asynccontextmanager
async def lifespan(app: FastAPI):
    bot_task = asyncio.create_task(run_bot())
    bot_data["is_running"] = True

    yield

    bot_data["is_running"] = False
    await bot_task
    await bot.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)
app.include_router(page_router)
app.include_router(chat_router)
app.include_router(websocket_router)


@dp.message()
async def handle_message(message: Message) -> None:
    user_id = message.from_user.id
    text = message.text
    username = message.from_user.username
    user = User(telegram_id=user_id, username=username)
    await message.answer(f"Hello, {message.from_user.full_name}")
    await message.answer(f"Ваше сообщение получено.\nЖдите ответа")
    async for session in get_session():
        bot_service = BotService(session)
        try:
            await bot_service.message_procces(user, text)
        except NoActiveAdmin:
            await message.answer(f"Сейчас нет администраторов, готовых вам ответить\nПожалуйста напишите позже")
        break


async def run_bot():
    await dp.start_polling(bot)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
