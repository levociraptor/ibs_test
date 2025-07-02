import json
from fastapi import WebSocket
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.chat_repository import ChatRepository


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, admin_id: int):
        await websocket.accept()
        self.active_connections[admin_id].append(websocket)
        print(f"Admin {admin_id} connected. Total connections: {len(self.active_connections[admin_id])}")

    def disconnect(self, admin_id, websocket: WebSocket):
        if admin_id in self.active_connections:
            self.active_connections[admin_id] = [
                ws for ws in self.active_connections[admin_id] if ws != websocket
            ]

            if not self.active_connections[admin_id]:
                del self.active_connections[admin_id]
                print(f"Admin {admin_id} disconnected. No more connections.")
            else:
                count_con = len(self.active_connections[admin_id])
                print(f"Admin {admin_id} disconnected. Remaining connections: {count_con}")

    async def send_json(self, data: dict, admin_id: int):
        for websocket in self.active_connections.get(admin_id, []):
            try:
                await websocket.send_json(data)
            except:
                self.disconnect(admin_id, websocket)


manager = ConnectionManager()
