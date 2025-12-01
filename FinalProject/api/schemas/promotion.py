from pydantic import BaseModel
from datetime import date


class PromotionBase(BaseModel):
    promo_code: str
    discount_percent: float
    expiration_date: date | None = None


class PromotionCreate(PromotionBase):
    pass


class PromotionUpdate(BaseModel):
    promo_code: str | None = None
    discount_percent: float | None = None
    expiration_date: date | None = None


class PromotionResponse(PromotionBase):
    id: int

    class ConfigDict:
        from_attributes = True
