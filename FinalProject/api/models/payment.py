from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..dependencies.database import Base


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    payment_type = Column(String(50), nullable=False)  # 'Card'|'Cash'|'UPI' etc.
    transaction_status = Column(String(50), nullable=False)  # 'Success'|'Failed'|'Pending'
    amount = Column(Float, nullable=False)
    order = relationship("Order", back_populates="payment")
