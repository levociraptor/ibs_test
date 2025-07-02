from app.config import settings

import jwt
from jwt import PyJWTError
from fastapi import Request
from fastapi.security import HTTPBearer
from fastapi import HTTPException

security = HTTPBearer()


async def get_current_admin(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        admin_id = payload.get("sub")
        admin_login = payload.get("login")

        if not admin_id or not admin_login:
            raise HTTPException(status_code=401, detail="Invalid token")

        return {"id": admin_id, "login": admin_login}
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


def get_current_admin_ws(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        admin_id = payload.get("sub")
        if admin_id is None:
            return None

        return {
            "id": admin_id,
            "login": payload.get("login")
        }
    except PyJWTError as e:
        return None
