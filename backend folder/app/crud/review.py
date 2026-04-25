from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func
from typing import List, Tuple

from app.models.review import Review
from app.schemas.review import ReviewCreate


def get_by_id(db: Session, review_id: int):
    return db.get(Review, review_id)


def get_by_pg_and_user(db: Session, pg_id: int, user_id: int):
    return db.scalar(
        select(Review).where(Review.pg_id == pg_id, Review.user_id == user_id)
    )


def create(db: Session, schema: ReviewCreate, user_id: int) -> Review:
    review = Review(
        user_id=user_id,
        pg_id=schema.pg_id,
        rating=schema.rating,
        comment=schema.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_pg_reviews(db: Session, pg_id: int, page: int = 1, page_size: int = 20) -> Tuple[List[Review], int]:
    total = db.scalar(select(func.count(Review.id)).where(Review.pg_id == pg_id))
    reviews = db.scalars(
        select(Review)
        .options(joinedload(Review.user))
        .where(Review.pg_id == pg_id)
        .order_by(Review.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return reviews, total


def delete(db: Session, review: Review) -> None:
    db.delete(review)
    db.commit()
