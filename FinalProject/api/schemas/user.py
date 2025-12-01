from pydantic import BaseModel


class UserBase(BaseModel):
    name: str
    email: str
    phone: str | None = None
    address: str | None = None
    role: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    role: str | None = None
    password: str | None = None


class UserResponse(UserBase):
    id: int

    class ConfigDict:
        from_attributes = True
