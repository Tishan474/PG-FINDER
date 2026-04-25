import math
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.crud import saved_pg as saved_crud
from app.crud import pg_listing as pg_crud
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.saved_pg import SavedPGResponse
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/saved", tags=["saved"])


@router.post("/{pg_id}", response_model=SavedPGResponse, status_code=status.HTTP_201_CREATED)
def save_pg(
    pg_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pg = pg_crud.get_by_id(db, pg_id)
    if not pg:
        raise HTTPException(status_code=404, detail="PG listing not found")

    existing = saved_crud.get_by_user_and_pg(db, current_user.id, pg_id)
    if existing:
        raise HTTPException(status_code=409, detail="Already saved")

    saved = saved_crud.save(db, user_id=current_user.id, pg_id=pg_id)
    # reload with relationship
    saved = saved_crud.get_by_user_and_pg(db, current_user.id, pg_id)
    return SavedPGResponse.model_validate(saved)


@router.delete("/{pg_id}", status_code=status.HTTP_204_NO_CONTENT)
def unsave_pg(
    pg_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    saved = saved_crud.get_by_user_and_pg(db, current_user.id, pg_id)
    if not saved:
        raise HTTPException(status_code=404, detail="Not in saved list")
    saved_crud.unsave(db, saved)


@router.get("", response_model=PaginatedResponse[SavedPGResponse])
def list_saved(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = saved_crud.get_user_saved(db, current_user.id, page, page_size)
    return {
        "items": [SavedPGResponse.model_validate(s) for s in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": math.ceil(total / page_size) if total else 0,
    }
