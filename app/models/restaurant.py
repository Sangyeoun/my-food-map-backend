from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, String, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.enums.restaurant_status import RestaurantStatus
from app.models.tag import Tag

# Design Ref: §3.3 — restaurant_tags association table (no separate model class)
restaurant_tags = Table(
    "restaurant_tags",
    Base.metadata,
    Column(
        "restaurant_id",
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Restaurant(Base):
    # Design Ref: §3.1, §3.3
    __tablename__ = "restaurants"
    __table_args__ = (CheckConstraint("my_rating BETWEEN 1 AND 5", name="ck_my_rating_range"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    google_place_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[RestaurantStatus] = mapped_column(nullable=False)
    my_rating: Mapped[int | None] = mapped_column(nullable=True)
    memo: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    tags: Mapped[list[Tag]] = relationship(
        secondary=restaurant_tags, back_populates="restaurants"
    )
