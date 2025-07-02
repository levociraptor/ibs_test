from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.depedinces.auth_depends import get_current_admin

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/page")


@router.get("/", response_class=HTMLResponse)
async def main_page(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin)
):
    return templates.TemplateResponse(
        "main.html", {
            "request": request,
            "admin": current_admin,
        }
    )


@router.get("/enter", response_class=HTMLResponse)
async def entry_page(
    request: Request,
):
    return templates.TemplateResponse("enter.html", {"request": request})


@router.get("/registration", response_class=HTMLResponse)
async def registration_page(
    request: Request,
):
    return templates.TemplateResponse("registration.html", {"request": request})


@router.get("/login_error")
async def login_error(request: Request, error: str = "invalid_credentials"):
    return templates.TemplateResponse(
        "error_page.html",
        {
            "request": request,
        }
    )
