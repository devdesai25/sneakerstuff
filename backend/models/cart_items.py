from backend.database import Base
from sqlalchemy.sql import func
from sqlalchemy import String, Integer, ForeignKey,DateTime, Column, UniqueConstraint
from sqlalchemy.orm import relationship

class CartItem(Base):
    
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, )
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)

    quantity = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "product_id",
            name="unique_user_product"
        ),
    )
    
    product = relationship("Product", back_populates="cart_items")