from backend.database import Base
from sqlalchemy import Column, ForeignKey, PrimaryKeyConstraint, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Drop(Base):
    __tablename__ = "drops"

    drop_id = Column(
        Integer, 
        primary_key=True,
        index=True,
    )

    product_id = Column(
        Integer, 
        ForeignKey("products.product_id"),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )

    opens_at = Column(
        DateTime(timezone=True), 
        nullable=False
    )
    
    closes_at = Column(
        DateTime(timezone=True), 
        nullable=False
    )

    drop_inventory = Column(
        Integer, 
        nullable=False
    )

    status = Column(
        String, 
        nullable=False
    )

    product = relationship(
        "Product",
        back_populates="drops",
    )

    entries = relationship(
        "Entry",
        back_populates="drop",
        cascade="all, delete-orphan"
    )