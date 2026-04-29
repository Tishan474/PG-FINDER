import enum
from datetime import datetime
from sqlalchemy import (
    String, Text, Enum, DateTime, Numeric, Integer,
    ForeignKey, Table, Column, Index, func, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
 
 
class GenderType(str, enum.Enum):
    boys = "boys"
    girls = "girls"
    coed = "co-ed"
 
 
PGAmenity = Table(
    "pg_amenities",
    Base.metadata,
    Column("pg_id", Integer, ForeignKey("pg_listings.id", ondelete="CASCADE"), primary_key=True),
    Column("amenity_id", Integer, ForeignKey("amenities.id", ondelete="CASCADE"), primary_key=True),
)
 
 
class Amenity(Base):
    __tablename__ = "amenities"
 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
 
    listings = relationship("PGListing", secondary=PGAmenity, back_populates="amenities")
 
 
class PGListing(Base):
    __tablename__ = "pg_listings"
 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    area: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, index=True)
    gender_type: Mapped[GenderType] = mapped_column(Enum(GenderType), nullable=False, index=True)
    rating: Mapped[float] = mapped_column(Numeric(3, 2), default=0.0, nullable=False)
    total_reviews: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
 
    phone: Mapped[str] = mapped_column(String(20), nullable=True)   # owner contact number
 
    # ── Photos stored as list of URLs ─────────────────────────────────────────
    # Uploaded once during PG creation, reused everywhere (cards, map popups, detail page)
    photos: Mapped[list] = mapped_column(JSON, default=list, nullable=True)
 
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
 
    owner = relationship("User", back_populates="listings")
    amenities = relationship("Amenity", secondary=PGAmenity, back_populates="listings")
    reviews = relationship("Review", back_populates="pg", cascade="all, delete-orphan")
    saved_by = relationship("SavedPG", back_populates="pg", cascade="all, delete-orphan")
 
    __table_args__ = (
        Index("ix_pg_listings_price_gender", "price", "gender_type"),
        Index("ix_pg_listings_city_area", "city", "area"),
    )
