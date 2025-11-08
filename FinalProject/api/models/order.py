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
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="orders")
    order_details = relationship(
        "OrderDetail", back_populates="order", cascade="all, delete-orphan"
    )
    payment = relationship(
        "Payment", back_populates="order", uselist=False, cascade="all, delete-orphan"
    )
