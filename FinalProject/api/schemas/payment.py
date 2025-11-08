from pydantic import BaseModel


class PaymentBase(BaseModel):
    payment_type: str
    transaction_status: str
    amount: float


class PaymentCreate(PaymentBase):
    order_id: int


class PaymentResponse(PaymentBase):
    id: int
    order_id: int

    class Config:
        orm_mode = True
