import math
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.redis_client import cache_get, cache_set, cache_delete_pattern
from app.crud import pg_listing as pg_crud
from app.crud import amenity as amenity_crud
from app.api.deps import get_current_user, get_optional_user, require_owner_or_admin
from app.models.user import User, UserRole
from app.models.pg_listing import GenderType
from app.schemas.pg_listing import (
    PGListingCreate, PGListingUpdate, PGListingResponse,
    PGListingFilters, MapPGResponse, AmenityResponse, AmenityCreate,
)
from app.schemas.common import PaginatedResponse
from app.core.config import settings

router = APIRouter(prefix="/pgs", tags=["pg-listings"])


@router.get("", response_model=PaginatedResponse[PGListingResponse])
async def list_pgs(
    search: Optional[str] = Query(None, max_length=100),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    gender_type: Optional[GenderType] = None,
    amenity_ids: Optional[List[int]] = Query(None),
    city: Optional[str] = Query(None, max_length=100),
    area: Optional[str] = Query(None, max_length=200),
    lat: Optional[float] = Query(None, ge=-90, le=90),
    lng: Optional[float] = Query(None, ge=-180, le=180),
    radius_km: Optional[float] = Query(None, gt=0, le=100),
    sort_by: Optional[str] = Query("created_at"),
    sort_order: Optional[str] = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    filters = PGListingFilters(
        search=search, min_price=min_price, max_price=max_price,
        gender_type=gender_type, amenity_ids=amenity_ids, city=city,
        area=area, lat=lat, lng=lng, radius_km=radius_km,
        sort_by=sort_by, sort_order=sort_order, page=page, page_size=page_size,
    )

    cache_key = f"pgs:list:{filters.model_dump_json()}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    items, total = pg_crud.get_list(db, filters)
    pages = math.ceil(total / page_size) if total else 0

    response = {
        "items": [PGListingResponse.model_validate(item).model_dump() for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }
    await cache_set(cache_key, response, ttl=120)
    return response


@router.get("/map", response_model=List[MapPGResponse])
async def map_pgs(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(5.0, gt=0, le=50),
    gender_type: Optional[GenderType] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    db: Session = Depends(get_db),
):
    cache_key = f"pgs:map:{lat}:{lng}:{radius_km}:{gender_type}:{min_price}:{max_price}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    results = pg_crud.get_map_pgs(db, lat, lng, radius_km, gender_type, min_price, max_price)
    validated = [MapPGResponse.model_validate(r).model_dump() for r in results]
    await cache_set(cache_key, validated, ttl=60)
    return validated


@router.get("/{pg_id}", response_model=PGListingResponse)
async def get_pg(pg_id: int, db: Session = Depends(get_db)):
    cache_key = f"pgs:detail:{pg_id}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    pg = pg_crud.get_by_id(db, pg_id)
    if not pg:
        raise HTTPException(status_code=404, detail="PG listing not found")

    response = PGListingResponse.model_validate(pg).model_dump()
    await cache_set(cache_key, response)
    return response


@router.post("", response_model=PGListingResponse, status_code=status.HTTP_201_CREATED)
async def create_pg(
    schema: PGListingCreate,
    db: Session = Depends(get_db),
):
    pg = pg_crud.create(db, schema, owner_id=1)
    return PGListingResponse.model_validate(pg)


@router.put("/{pg_id}", response_model=PGListingResponse)
async def update_pg(
    pg_id: int,
    schema: PGListingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pg = pg_crud.get_by_id(db, pg_id)
    if not pg:
        raise HTTPException(status_code=404, detail="PG listing not found")
    if pg.created_by != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized to edit this listing")
    updated = pg_crud.update(db, pg, schema)
    await cache_delete_pattern(f"pgs:detail:{pg_id}")
    await cache_delete_pattern("pgs:list:*")
    await cache_delete_pattern("pgs:map:*")
    return PGListingResponse.model_validate(updated)


@router.delete("/{pg_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pg(
    pg_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pg = pg_crud.get_by_id(db, pg_id)
    if not pg:
        raise HTTPException(status_code=404, detail="PG listing not found")
    if pg.created_by != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this listing")
    pg_crud.delete(db, pg)
    await cache_delete_pattern(f"pgs:detail:{pg_id}")
    await cache_delete_pattern("pgs:list:*")
    await cache_delete_pattern("pgs:map:*")


# ── Amenities ──────────────────────────────────────────────────────────────────

@router.get("/amenities/all", response_model=List[AmenityResponse])
def list_amenities(db: Session = Depends(get_db)):
    return amenity_crud.get_all(db)


@router.post("/amenities", response_model=AmenityResponse, status_code=201)
def create_amenity(
    schema: AmenityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner_or_admin),
):
    existing = amenity_crud.get_by_name(db, schema.name)
    if existing:
        raise HTTPException(status_code=409, detail="Amenity already exists")
    return amenity_crud.create(db, schema)
