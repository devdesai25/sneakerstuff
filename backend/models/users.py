from backend.database import Base
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__='users'

    id = Column(Integer, primary_key=True, index=True)

    username = Column(
        String, 
        unique=True,
        index=True,
        nullable=False
    )
    
    hashed_password = Column(
        String,
        nullable=False
    )

    role = Column(
        String,
        nullable=False,
        server_default="user"
    )

    entries = relationship(
        "Entry",
        back_populates="user"
    )

    orders = relationship(
        "Order",
        back_populates="user"
    )