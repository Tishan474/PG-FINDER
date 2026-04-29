import math
import uuid
import aiofiles
from pathlib import Path
from typing import Optional, List
from decimal import Decimal
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
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
 
# ── Photo upload config ────────────────────────────────────────────────────────
UPLOAD_DIR      = Path("uploads/pg_photos")
ALLOWED_TYPES   = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE   = 5 * 1024 * 1024   # 5 MB
MAX_PHOTOS      = 8
BASE_URL        = "https://pg-finder-production.up.railway.app"  # change to your domain in production
 
 
async def save_photos(photos: List[UploadFile]) -> List[str]:
    """
    Validates and saves uploaded photos to disk.
    Returns a list of public URLs.
    Photos are saved ONCE here — the same URLs are stored in DB
    and reused everywhere (listing card, detail page, etc.)
    """
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    urls = []
 
    for photo in photos:
        # Validate type
        if photo.content_type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"'{photo.filename}' is not an allowed type. Use JPG, PNG or WEBP."
            )
 
        # Read and validate size
        contents = await photo.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"'{photo.filename}' exceeds the 5 MB limit."
            )
 
        # Save with a unique filename so the same photo uploaded twice
        # never overwrites the original — each upload gets its own file.
        ext      = Path(photo.filename).suffix.lower() or ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"
        path     = UPLOAD_DIR / filename
 
        async with aiofiles.open(path, "wb") as f:
            await f.write(contents)
 
        urls.append(f"{BASE_URL}/uploads/pg_photos/{filename}")
 
    return urls
 
 
# ── List PGs ───────────────────────────────────────────────────────────────────
 
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
 
 
# ── Map PGs ────────────────────────────────────────────────────────────────────
 
@router.get("/map", response_model=List[MapPGResponse])
async def map_pgs(
    lat: Optional[float] = Query(None, ge=-90, le=90),
    lng: Optional[float] = Query(None, ge=-180, le=180),
    radius_km: Optional[float] = Query(None, gt=0, le=50),
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
    await cache_set(cache_key, validated, ttl=10)  # short TTL so new PGs appear quickly
    return validated
 
 
# ── Get single PG ──────────────────────────────────────────────────────────────
 
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
 
 
# ── Create PG (with photos) ────────────────────────────────────────────────────
 
@router.post("", response_model=PGListingResponse, status_code=status.HTTP_201_CREATED)
async def create_pg(
    # Text fields — received as multipart/form-data from the frontend
    name:        str        = Form(...),
    area:        str        = Form(...),
    city:        str        = Form(...),
    price:       Decimal    = Form(...),
    latitude:    float      = Form(...),
    longitude:   float      = Form(...),
    gender_type: GenderType = Form(...),
    description: str        = Form(""),
    phone:       Optional[str] = Form(None),   # owner contact number
 
    # Photos — optional list of image files, uploaded ONCE here and stored as URLs
    # The same URLs are reused on listing cards, detail pages, map popups — everywhere.
    photos: Optional[List[UploadFile]] = File(None),
 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Validate photo count
    if photos and len(photos) > MAX_PHOTOS:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_PHOTOS} photos allowed per listing."
        )
 
    # Save photos to disk once — returns list of public URLs
    # e.g. ["http://127.0.0.1:8000/uploads/pg_photos/abc123.jpg", ...]
    photo_urls: List[str] = []
    if photos:
        # Filter out empty file inputs (browser sometimes sends blank UploadFile)
        valid_photos = [p for p in photos if p.filename]
        if valid_photos:
            photo_urls = await save_photos(valid_photos)
 
    # Build the schema — photos stored as URL list in DB
    schema = PGListingCreate(
        name=name,
        area=area,
        city=city,
        price=price,
        latitude=latitude,
        longitude=longitude,
        gender_type=gender_type,
        description=description,
        phone=phone,
        photos=photo_urls,      # ← stored once, reused everywhere
    )
 
    pg = pg_crud.create(db, schema, owner_id=current_user.id)
    await cache_delete_pattern("pgs:list:*")
    await cache_delete_pattern("pgs:map:*")  # clear map cache so new PG appears immediately
    return PGListingResponse.model_validate(pg)
 
 
# ── Update PG ──────────────────────────────────────────────────────────────────
 
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
 
 
# ── Delete PG ──────────────────────────────────────────────────────────────────
 
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
