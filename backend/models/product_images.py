from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class ProductImage(Base):
    __tablename__ = "product_images"

    image_id = Column(Integer, primary_key=True, index=True)

    product_id = Column(Integer, ForeignKey=("products.product_id"), nullable=False)

    image_url = Column(String, nullable=False)

    