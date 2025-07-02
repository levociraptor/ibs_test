from datetime import datetime
from datetime import timedelta
from datetime import timezone

from app.schemas.admin_schema import AdminData
from app.repositories.admin_repository import AdminRepository
from app.exceptions import AdminNotFound
from app.exceptions import WrongPassword
from app.exceptions import AdminAlredyExists
from app.config import settings

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
import jwt


class AdminService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.admin_repository = AdminRepository(session)

    async def reg_admin(self, reg_data: AdminData) -> str:
        admin = await self.admin_repository.get_admin_by_login(reg_data.login)
        if admin:
            raise AdminAlredyExists
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password = pwd_context.hash(reg_data.password)
        admin = await self.admin_repository.add_admin(
            admin_data=reg_data,
            hash_password=password,
        )
        jwt_token = self._create_access(admin.id, admin.name)
        return jwt_token

    async def validate_admin(self, reg_data: AdminData) -> str:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        plain_password = reg_data.password
        admin = await self.admin_repository.get_admin_by_login(reg_data.login)
        if not admin:
            raise AdminNotFound
        if not pwd_context.verify(plain_password, admin.hashed_password):
            raise WrongPassword
        jwt_token = self._create_access(admin.id, admin.name)
        return jwt_token

    def _create_access(self, admin_id: int, admin_login: str) -> str:
        exp = datetime.now(timezone.utc) + timedelta(settings.ACCESS_TOKEN_EXPIRE_DAYS)
        iat = datetime.now(timezone.utc)
        payload = {
            "sub": str(admin_id),
            "login": admin_login,
            "iat": iat,
            "exp": exp,
        }
        return jwt.encode(payload, settings.JWT_SECRET, settings.JWT_ALGORITHM)
