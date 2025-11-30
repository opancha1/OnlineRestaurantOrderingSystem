from typing import Optional
from pydantic import BaseModel


class OrderDetailBase(BaseModel):
    order_id: int
    menu_item_id: int
    quantity: int


class OrderDetailCreate(OrderDetailBase):
    pass


class OrderDetailUpdate(BaseModel):
    order_id: Optional[int] = None
    menu_item_id: Optional[int] = None
    quantity: Optional[int] = None


class OrderDetail(OrderDetailBase):
    id: int
    unit_price: Optional[float] = None
    line_total: Optional[float] = None

    class ConfigDict:
        from_attributes = True
