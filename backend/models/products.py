from backend.database import Base
from sqlalchemy import Column, String, Float, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .users import User
class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)

    name = Column(String, unique = True, index=True, nullable= False)
    description = Column(String, nullable=False)

    stock = Column(Integer, default=0, nullable=False)
    price = Column(Float, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    created_by = Column(Integer, ForeignKey("users.id"),nullable=False)

    images = Column(String, nullable= False)

    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product", cascade="all, delete-orphan")
    drops = relationship("Drop", back_populates="product")