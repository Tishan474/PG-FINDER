from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func
from typing import List, Tuple, Optional

from app.models.saved_pg import SavedPG
from app.models.pg_listing import PGListing


def get_by_user_and_pg(db: Session, user_id: int, pg_id: int) -> Optional[SavedPG]:
    return db.scalar(
        select(SavedPG).where(SavedPG.user_id == user_id, SavedPG.pg_id == pg_id)
    )


def save(db: Session, user_id: int, pg_id: int) -> SavedPG:
    saved = SavedPG(user_id=user_id, pg_id=pg_id)
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved


def unsave(db: Session, saved: SavedPG) -> None:
    db.delete(saved)
    db.commit()


def get_user_saved(db: Session, user_id: int, page: int = 1, page_size: int = 20) -> Tuple[List[SavedPG], int]:
    total = db.scalar(select(func.count(SavedPG.id)).where(SavedPG.user_id == user_id))
    items = db.scalars(
        select(SavedPG)
        .options(
            selectinload(SavedPG.pg).selectinload(PGListing.amenities)
        )
        .where(SavedPG.user_id == user_id)
        .order_by(SavedPG.saved_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return items, total
