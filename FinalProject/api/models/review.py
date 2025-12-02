from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..dependencies.database import Base


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1..5
    comment = Column(String(255))
    order = relationship("Order", back_populates="reviews")
    menu_item = relationship("MenuItem", back_populates="reviews")
