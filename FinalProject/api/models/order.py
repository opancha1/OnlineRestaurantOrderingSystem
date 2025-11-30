from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from ..dependencies.database import Base


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    order_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default="Pending")
    total_price = Column(Float)
    tracking_number = Column(String(100))
    # Registered users have a user_id; guests store contact fields instead.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    guest_name = Column(String(100))
    guest_email = Column(String(120))
    guest_phone = Column(String(20))
    user = relationship("User", back_populates="orders")
    order_details = relationship(
        "OrderDetail", back_populates="order", cascade="all, delete-orphan"
    )
    payment = relationship(
        "Payment", back_populates="order", uselist=False, cascade="all, delete-orphan"
    )
