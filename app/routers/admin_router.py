from fastapi import APIRouter, Form
from fastapi import Depends
from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.admin_schema import AdminData
from app.services.admin_service import AdminService
from app.database import get_session
from app.exceptions import AdminNotFound
from app.exceptions import WrongPassword
from app.exceptions import AdminAlredyExists

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/reg_admin")
async def register_admin(
    request: Request,
    login: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    reg_data = AdminData(login=login, password=password)
    try:
        jwt_token = await AdminService(session).reg_admin(reg_data)
        response = RedirectResponse(url="/page/", status_code=303)
        response.set_cookie(
            key="access_token",
            value=jwt_token,
        )
        return response
    except AdminAlredyExists:
        error_type = "invalid_login"
        error_message = "Админ с таким логином уже существует"
        return templates.TemplateResponse(
            "try_again.html",
            {
                "request": request,
                "error_type": error_type,
                "error_message": error_message,
            }
        )


@router.post("/enter_admin")
async def enter_admin(
    request: Request,
    login: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    enter_data = AdminData(login=login, password=password)
    try:
        jwt_token = await AdminService(session).validate_admin(enter_data)
        response = RedirectResponse(url="/page/", status_code=303)
        response.set_cookie(
            key="access_token",
            value=jwt_token,
            httponly=True,
            path="/",
            samesite="lax",
        )
        return response
    except AdminNotFound:
        error_type = "invalid_login"
        error_message = "Админа с таким логином не существует"
        return templates.TemplateResponse(
            "try_again.html",
            {
                "request": request,
                "error_type": error_type,
                "error_message": error_message,
            }
        )
    except WrongPassword:
        error_type = "invalid_password"
        error_message = "Пароль введен неверно"
        return templates.TemplateResponse(
            "try_again.html",
            {
                "request": request,
                "error_type": error_type,
                "error_message": error_message,
            }
        )
