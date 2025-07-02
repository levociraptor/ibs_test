from pydantic import BaseModel


class ChatSchema(BaseModel):
    id: int
    user_id: int
    username: str
    last_message: str | None = None

    class Config:
        from_attributes = True
