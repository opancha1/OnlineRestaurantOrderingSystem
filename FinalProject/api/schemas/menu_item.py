from pydantic import BaseModel


class MenuItemBase(BaseModel):
    name: str
    description: str | None = None
    price: float
    category: str | None = None
    calories: int | None = None
    stock: int | None = 0


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    category: str | None = None
    calories: int | None = None
    stock: int | None = None


class MenuItemResponse(MenuItemBase):
    id: int

    class Config:
        orm_mode = True
