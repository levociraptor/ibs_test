from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.admin_schema import AdminData
from app.models import AdminUserORM


class AdminRepository():
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_admin(self, hash_password: str, admin_data: AdminData) -> AdminUserORM:
        admin = AdminUserORM(
            name=admin_data.login,
            hashed_password=hash_password,
        )
        self.session.add(
            admin
        )
        await self.session.commit()
        await self.session.refresh(admin)
        return admin

    async def get_admin_by_login(self, login: str) -> AdminUserORM:
        admin = await self.session.execute(
            select(AdminUserORM).where(AdminUserORM.name == login)
        )
        return admin.scalar_one_or_none()
