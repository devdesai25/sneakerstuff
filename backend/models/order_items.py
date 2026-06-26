from backend.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship

class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id = Column(Integer, primary_key=True, index=True)
    
    product_id = Column(
        Integer, 
        ForeignKey("products.product_id"), 
        index=True
    )
    order_id = Column(
        Integer, 
        ForeignKey("orders.order_id"),
        index=True
        )
    
    quantity = Column(Integer, default=1)

    unit_price = Column(Float, nullable=False)

    subtotal = Column(Float)

    order = relationship(
        "Order",
        back_populates="order_items"
    )

    product = relationship(
        "Product",
        back_populates="order_items"
    )