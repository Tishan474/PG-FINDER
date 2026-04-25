import math
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.redis_client import cache_delete_pattern
from app.crud import review as review_crud
from app.crud import pg_listing as pg_crud
from app.api.deps import get_current_user
from app.models.user import User, UserRole
from app.schemas.review import ReviewCreate, ReviewResponse
from app.schemas.common import PaginatedResponse

router = APIRouter(tags=["reviews"])


@router.post("/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    schema: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pg = pg_crud.get_by_id(db, schema.pg_id)
    if not pg:
        raise HTTPException(status_code=404, detail="PG listing not found")

    existing = review_crud.get_by_pg_and_user(db, schema.pg_id, current_user.id)
    if existing:
        raise HTTPException(status_code=409, detail="You have already reviewed this PG")

    review = review_crud.create(db, schema, user_id=current_user.id)
    pg_crud.update_rating(db, schema.pg_id)

    await cache_delete_pattern(f"pgs:detail:{schema.pg_id}")
    await cache_delete_pattern("pgs:list:*")

    resp = ReviewResponse.model_validate(review)
    resp.user_name = current_user.name
    return resp


@router.get("/pgs/{pg_id}/reviews", response_model=PaginatedResponse[ReviewResponse])
def get_pg_reviews(
    pg_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    pg = pg_crud.get_by_id(db, pg_id)
    if not pg:
        raise HTTPException(status_code=404, detail="PG listing not found")

    reviews, total = review_crud.get_pg_reviews(db, pg_id, page, page_size)
    items = []
    for r in reviews:
        resp = ReviewResponse.model_validate(r)
        resp.user_name = r.user.name if r.user else None
        items.append(resp)

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": math.ceil(total / page_size) if total else 0,
    }


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = review_crud.get_by_id(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.user_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    pg_id = review.pg_id
    review_crud.delete(db, review)
    pg_crud.update_rating(db, pg_id)
    await cache_delete_pattern(f"pgs:detail:{pg_id}")
    await cache_delete_pattern("pgs:list:*")
