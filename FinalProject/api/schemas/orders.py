from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class OrderBase(BaseModel):
    status: Optional[str] = None
    total_price: float
    tracking_number: Optional[str] = None
    user_id: int


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    total_price: Optional[float] = None
    tracking_number: Optional[str] = None


class Order(OrderBase):
    id: int
    order_date: Optional[datetime] = None

    class ConfigDict:
        from_attributes = True
