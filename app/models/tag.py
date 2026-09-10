from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Tag(Base):
    # Design Ref: §3.1 — Restaurant N:M Tag
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    restaurants: Mapped[list["Restaurant"]] = relationship(
        secondary="restaurant_tags", back_populates="tags"
    )
