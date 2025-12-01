from pydantic import BaseModel


class UserBase(BaseModel):
    name: str
    email: str
    phone: str | None = None
    address: str | None = None
    role: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int

    class ConfigDict:
        from_attributes = True
