from pydantic import BaseModel
from typing import List
from .order_detail import OrderDetailResponse


class OrderBase(BaseModel):
    status: str | None = "Pending"
    total_price: float | None = None
    tracking_number: str | None = None


class OrderCreate(BaseModel):
    user_id: int
    items: List[dict]  # [{ "menu_item_id": 1, "quantity": 2 }, ...]


class OrderResponse(OrderBase):
    id: int
    user_id: int
    order_details: List[OrderDetailResponse] = []

    class Config:
        orm_mode = True
