from pydantic import BaseModel
from datetime import date


class PromotionBase(BaseModel):
    promo_code: str
    discount_percent: float
    expiration_date: date | None = None


class PromotionCreate(PromotionBase):
    pass


class PromotionResponse(PromotionBase):
    id: int

    class ConfigDict:
        from_attributes = True
