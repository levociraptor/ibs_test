from pydantic import BaseModel


class AdminData(BaseModel):
    password: str
    login: str
