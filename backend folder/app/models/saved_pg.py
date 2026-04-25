from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class SavedPG(Base):
    __tablename__ = "saved_pgs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    pg_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pg_listings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    saved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user = relationship("User", back_populates="saved_pgs")
    pg = relationship("PGListing", back_populates="saved_by")

    __table_args__ = (
        UniqueConstraint("user_id", "pg_id", name="uq_saved_pgs_user_id_pg_id"),
    )
