from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..dependencies.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    phone = Column(String(20))
    address = Column(String(255))
    password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # 'customer', 'staff', 'admin'

    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="user")
