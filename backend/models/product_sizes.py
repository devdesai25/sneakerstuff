from backend.database import Base
from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

class ProductSize(Base):

    __tablename__ = "product_sizes"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    product_id = Column(
        Integer,
        ForeignKey("products.product_id"),
        nullable=False
    )

    size = Column(
        String,
        nullable=False
    )

    stock = Column(
        Integer,
        default=0,
        nullable=False
    )

    product = relationship(
        "Product",
        back_populates="sizes"
    )

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "size",
            name="unique_product_size"
        ),
    )
