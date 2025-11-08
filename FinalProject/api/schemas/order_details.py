from pydantic import BaseModel


class OrderDetailBase(BaseModel):
    menu_item_id: int
    quantity: int


class OrderDetailCreate(OrderDetailBase):
    pass


class OrderDetailResponse(OrderDetailBase):
    id: int
    order_id: int

    class Config:
        orm_mode = True
