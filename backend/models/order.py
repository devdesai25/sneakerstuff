from backend.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer, 
        ForeignKey("users.id"), 
        nullable=False
    )

    total_amount = Column(Float, nullable=False)

    status = Column(String, nullable=False, index=True,)

    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now()
    )

    expires_at = Column(
        DateTime(timezone=True), 
        nullable= False 
    )

    paid_at = Column(DateTime(timezone=True))

    payment_id = Column(String)

    address = Column(String, nullable=False)

    order_items = relationship(
        "OrderItem", 
        back_populates="order", 
        cascade="all, delete-orphan"
        )
    
    reservation = relationship(
        "Reservation",
        back_populates="order",
        uselist=False
    )

    user = relationship(
        "User",
        back_populates="orders"
    )