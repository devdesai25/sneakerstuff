from backend.database import Base
from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Reservation(Base):

    __tablename__ = "reservations"

    reservation_id = Column(
        Integer, 
        primary_key=True,
        index=True
    )

    entry_id = Column(
        Integer, 
        ForeignKey("entries.entry_id"), 
        unique=True,
        nullable=False
        )
    
    order_id = Column(
        Integer, 
        ForeignKey("orders.order_id"), 
        unique=True,
        nullable=False
    )
    
    status = Column(
        String, 
        index=True, 
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    
    expiry_at = Column(
        DateTime(timezone=True),
        nullable=False
    )
    
    order = relationship(
        "Order",
        back_populates="reservation"
    )

    entry = relationship(
        "Entry",
        back_populates="reservation"
    )
