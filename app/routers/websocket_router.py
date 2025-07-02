from fastapi import WebSocket
from fastapi import WebSocketDisconnect
from fastapi import Cookie

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.services.chat_service import ChatService
from app.services.connection_service import manager
from app.depedinces.auth_depends import get_current_admin_ws

router = APIRouter()


@router.websocket("/ws/admin")
async def websocket_endpoint(
    websocket: WebSocket,
    access_token: str | None = Cookie(default=None),
    session: AsyncSession = Depends(get_session)
):
    try:
        admin = get_current_admin_ws(access_token)
        if not admin:
            await websocket.close(code=1008)
            return
    except Exception:
        await websocket.close(code=1008)
        return
    admin_id = int(admin["id"])
    await manager.connect(websocket, admin_id)

    try:
        while True:
            data = await websocket.receive_json()
            if data['type'] == 'send':
                chat_id = data['chat_id']
                content = data['content']
                chat_service = ChatService(session)
                await chat_service.send_message(
                    admin_id=admin_id,
                    chat_id=chat_id,
                    content=content
                )

    except WebSocketDisconnect:
        manager.disconnect(admin_id, websocket)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        manager.disconnect(admin_id, websocket)
