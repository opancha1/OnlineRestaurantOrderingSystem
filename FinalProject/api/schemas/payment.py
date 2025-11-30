from pydantic import BaseModel


class PaymentBase(BaseModel):
    payment_type: str
    transaction_status: str
    amount: float


class PaymentCreate(PaymentBase):
    order_id: int


class PaymentUpdate(BaseModel):
    payment_type: str | None = None
    transaction_status: str | None = None
    amount: float | None = None


class PaymentResponse(PaymentBase):
    id: int
    order_id: int

    class ConfigDict:
        from_attributes = True
