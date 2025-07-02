from datetime import datetime
from enum import Enum

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy import TIMESTAMP
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import Text
from sqlalchemy.sql import func


Base = declarative_base()


class Status(Enum):
    NEW = "new"
    PENDING = "pending"
    DONE = "done"


class AdminUserORM(Base):
    __tablename__ = "AdminUser"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str] = mapped_column(unique=True)
    banned_at: Mapped[datetime] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        server_default=func.now(),
        onupdate=func.current_timestamp(),
    )
    chats: Mapped[list["ChatORM"]] = relationship(back_populates="admin")


class UserORM(Base):
    __tablename__ = "User"
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(nullable=True)
    banned_at: Mapped[datetime] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        server_default=func.now(),
        onupdate=func.current_timestamp(),
    )
    chats: Mapped[list["ChatORM"]] = relationship(back_populates="user")


class ChatORM(Base):
    __tablename__ = "Chat"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("User.id"))
    admin_id: Mapped[int] = mapped_column(ForeignKey("AdminUser.id"), nullable=True)
    status: Mapped[Status] = mapped_column(
        SqlEnum(Status),
        nullable=False,
        default=Status.NEW,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        server_default=func.now(),
        onupdate=func.current_timestamp(),
    )
    user: Mapped["UserORM"] = relationship(back_populates="chats")
    admin: Mapped["AdminUserORM"] = relationship(back_populates="chats")
    messages: Mapped[list["MessageORM"]] = relationship(
        back_populates="chat",
        order_by="MessageORM.created_at"
    )


class MessageORM(Base):
    __tablename__ = "Message"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("Chat.id"))
    type_message: Mapped[str] = mapped_column()
    sender_id: Mapped[int] = mapped_column()
    content: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )
    chat: Mapped["ChatORM"] = relationship(back_populates="messages")
