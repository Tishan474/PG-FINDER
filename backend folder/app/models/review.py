from datetime import datetime
from sqlalchemy import Integer, Text, Numeric, ForeignKey, DateTime, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    pg_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pg_listings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rating: Mapped[float] = mapped_column(Numeric(3, 1), nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user = relationship("User", back_populates="reviews")
    pg = relationship("PGListing", back_populates="reviews")

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_reviews_rating_range"),
    )
