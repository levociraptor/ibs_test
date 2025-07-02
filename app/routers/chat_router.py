from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.depedinces.auth_depends import get_current_admin
from app.database import get_session
from app.services.chat_service import ChatService

router = APIRouter()


@router.get("/admin/chats", response_model=list[dict])
async def get_admin_chats(
    current_admin: dict = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session)
):
    admin_id = int(current_admin["id"])
    service = ChatService(session)
    chats = await service.get_admin_chats(admin_id)
    return chats
