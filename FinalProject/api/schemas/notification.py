from pydantic import BaseModel
from typing import Optional


class NotificationBase(BaseModel):
    order_id: Optional[int] = None
    channel: Optional[str] = "mock"
    status: Optional[str] = "sent"
    message: str


class NotificationCreate(NotificationBase):
    pass


class NotificationResponse(NotificationBase):
    id: int

    class ConfigDict:
        from_attributes = True
