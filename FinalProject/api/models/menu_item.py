from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from ..dependencies.database import Base


class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    price = Column(Float, nullable=False)
    category = Column(String(50))
    calories = Column(Integer)
    stock = Column(Integer, nullable=False, default=0)
    order_details = relationship("OrderDetail", back_populates="menu_item")
    reviews = relationship("Review", back_populates="menu_item")
