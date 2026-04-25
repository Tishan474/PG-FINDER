from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional

from app.models.pg_listing import Amenity
from app.schemas.pg_listing import AmenityCreate


def get_all(db: Session) -> List[Amenity]:
    return db.scalars(select(Amenity).order_by(Amenity.name)).all()


def get_by_id(db: Session, amenity_id: int) -> Optional[Amenity]:
    return db.get(Amenity, amenity_id)


def get_by_name(db: Session, name: str) -> Optional[Amenity]:
    return db.scalar(select(Amenity).where(Amenity.name == name))


def create(db: Session, schema: AmenityCreate) -> Amenity:
    amenity = Amenity(name=schema.name)
    db.add(amenity)
    db.commit()
    db.refresh(amenity)
    return amenity
