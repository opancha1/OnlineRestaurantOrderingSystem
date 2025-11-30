from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from .order_details import OrderDetail as OrderDetailResponse


class OrderItem(BaseModel):
    menu_item_id: int
    quantity: int = Field(gt=0, description="Quantity must be greater than zero")


class OrderBase(BaseModel):
    status: Optional[str] = "Pending"
    total_price: Optional[float] = None
    tracking_number: Optional[str] = None
    user_id: Optional[int] = None
    guest_name: Optional[str] = None
    guest_email: Optional[EmailStr] = None
    guest_phone: Optional[str] = None


class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItem]


class GuestOrderCreate(BaseModel):
    guest_name: str
    guest_email: Optional[EmailStr] = None
    guest_phone: Optional[str] = None
    items: List[OrderItem]


class OrderResponse(OrderBase):
    id: int
    order_date: Optional[datetime] = None
    order_details: List[OrderDetailResponse] = []

    class ConfigDict:
        from_attributes = True
