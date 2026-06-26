from backend.database import Base
from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship

class Entry(Base):

    __tablename__="entries"

    entry_id = Column(
        Integer, 
        primary_key=True,
        index=True
    )

    drop_id = Column(
        Integer, 
        ForeignKey("drops.drop_id"), 
        index=True,
        nullable=False
    )

    user_id = Column(
        Integer, 
        ForeignKey("users.id"),
        nullable=False
    )

    ranking = Column(
        Integer, 
        index=True, 
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="entries"
    )

    drop = relationship(
        "Drop",
        back_populates="entries"
    )

    reservation = relationship(
        "Reservation",
        back_populates="entry",
        uselist=False
    )

    __table_args__ = (
        UniqueConstraint(
        "drop_id",
        "user_id",
        name="unique_entry_and_user"
        ),
    )

    Index(
        "idx_drop_ranking",
        "drop_id",
        "ranking"
    )