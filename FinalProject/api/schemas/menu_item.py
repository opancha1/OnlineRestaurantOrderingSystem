from pydantic import BaseModel


class MenuItemBase(BaseModel):
    name: str
    description: str | None = None
    price: float
    category: str | None = None
    calories: int | None = None


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemResponse(MenuItemBase):
    id: int

    class Config:
        orm_mode = True
