from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func, and_, or_, cast, Float
from sqlalchemy.dialects.postgresql import ARRAY
from typing import Optional, List, Tuple
from decimal import Decimal

from app.models.pg_listing import PGListing, Amenity, PGAmenity, GenderType
from app.schemas.pg_listing import PGListingCreate, PGListingUpdate, PGListingFilters
from app.core.config import settings


def _make_point(lat: float, lng: float):
    return ST_SetSRID(ST_MakePoint(lng, lat), 4326)


def get_by_id(db: Session, pg_id: int) -> Optional[PGListing]:
    return db.scalar(
        select(PGListing)
        .options(selectinload(PGListing.amenities), selectinload(PGListing.owner))
        .where(PGListing.id == pg_id)
    )


def create(db: Session, schema: PGListingCreate, owner_id: int) -> PGListing:
    amenities = db.scalars(
        select(Amenity).where(Amenity.id.in_(schema.amenity_ids))
    ).all() if schema.amenity_ids else []

    pg = PGListing(
        name=schema.name,
        description=schema.description,
        area=schema.area,
        city=schema.city,
        latitude=float(schema.latitude),
        longitude=float(schema.longitude),
        location=f"{schema.latitude},{schema.longitude}",
        price=schema.price,
        gender_type=schema.gender_type,
        created_by=owner_id,
        amenities=list(amenities),
    )
    db.add(pg)
    db.commit()
    db.refresh(pg)
    return get_by_id(db, pg.id)


def update(db: Session, pg: PGListing, schema: PGListingUpdate) -> PGListing:
    data = schema.model_dump(exclude_unset=True, exclude={"amenity_ids"})
    for key, value in data.items():
        setattr(pg, key, value)

    if schema.latitude is not None or schema.longitude is not None:
        lat = float(schema.latitude or pg.latitude)
        lng = float(schema.longitude or pg.longitude)
        pg.location = f"{lat},{lng}"

    if schema.amenity_ids is not None:
        amenities = db.scalars(
            select(Amenity).where(Amenity.id.in_(schema.amenity_ids))
        ).all()
        pg.amenities = list(amenities)

    db.commit()
    db.refresh(pg)
    return get_by_id(db, pg.id)


def delete(db: Session, pg: PGListing) -> None:
    db.delete(pg)
    db.commit()


def get_list(
    db: Session, filters: PGListingFilters
) -> Tuple[List[dict], int]:
    distance_col = None

    stmt = select(PGListing).options(selectinload(PGListing.amenities))

    if filters.lat and filters.lng and filters.radius_km:
        user_point = _make_point(filters.lat, filters.lng)
        stmt = stmt.where(
            ST_DWithin(
                cast(PGListing.location, type_=__import__('geoalchemy2').Geography),
                cast(user_point, type_=__import__('geoalchemy2').Geography),
                filters.radius_km * 1000,
            )
        )
        distance_col = ST_Distance(
            cast(PGListing.location, type_=__import__('geoalchemy2').Geography),
            cast(user_point, type_=__import__('geoalchemy2').Geography),
        )

    if filters.search:
        term = f"%{filters.search.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(PGListing.name).like(term),
                func.lower(PGListing.area).like(term),
                func.lower(PGListing.city).like(term),
            )
        )

    if filters.min_price is not None:
        stmt = stmt.where(PGListing.price >= filters.min_price)
    if filters.max_price is not None:
        stmt = stmt.where(PGListing.price <= filters.max_price)
    if filters.gender_type:
        stmt = stmt.where(PGListing.gender_type == filters.gender_type)
    if filters.city:
        stmt = stmt.where(func.lower(PGListing.city) == filters.city.lower())
    if filters.area:
        stmt = stmt.where(func.lower(PGListing.area).like(f"%{filters.area.lower()}%"))
    if filters.amenity_ids:
        for amenity_id in filters.amenity_ids:
            stmt = stmt.where(
                PGListing.amenities.any(Amenity.id == amenity_id)
            )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.scalar(count_stmt)

    # Sorting
    if filters.sort_by == "distance" and distance_col is not None:
        order = distance_col if filters.sort_order == "asc" else distance_col.desc()
    elif filters.sort_by == "price":
        order = PGListing.price if filters.sort_order == "asc" else PGListing.price.desc()
    elif filters.sort_by == "rating":
        order = PGListing.rating if filters.sort_order == "asc" else PGListing.rating.desc()
    else:
        order = PGListing.created_at.desc()

    stmt = stmt.order_by(order)

    page_size = min(filters.page_size, settings.MAX_PAGE_SIZE)
    offset = (filters.page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)

    rows = db.scalars(stmt).all()

    results = []
    for pg in rows:
        pg_dict = {c.name: getattr(pg, c.name) for c in pg.__table__.columns}
        pg_dict["amenities"] = pg.amenities
        if distance_col is not None:
            dist_val = db.scalar(
                select(distance_col.label("d")).where(PGListing.id == pg.id)
            )
            pg_dict["distance_km"] = round(dist_val / 1000, 2) if dist_val else None
        else:
            pg_dict["distance_km"] = None
        results.append(pg_dict)

    return results, total


def get_map_pgs(
    db: Session,
    lat: float,
    lng: float,
    radius_km: float,
    gender_type: Optional[GenderType] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
) -> List[dict]:
    from geoalchemy2 import Geography
    from sqlalchemy import cast as sa_cast

    user_point = _make_point(lat, lng)
    distance_col = ST_Distance(
        sa_cast(PGListing.location, Geography),
        sa_cast(user_point, Geography),
    )

    stmt = (
        select(PGListing, distance_col.label("distance_m"))
        .where(
            ST_DWithin(
                sa_cast(PGListing.location, Geography),
                sa_cast(user_point, Geography),
                radius_km * 1000,
            )
        )
    )

    if gender_type:
        stmt = stmt.where(PGListing.gender_type == gender_type)
    if min_price is not None:
        stmt = stmt.where(PGListing.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(PGListing.price <= max_price)

    stmt = stmt.order_by(distance_col).limit(200)
    rows = db.execute(stmt).all()

    results = []
    for pg, dist in rows:
        results.append({
            "id": pg.id,
            "name": pg.name,
            "latitude": float(pg.latitude),
            "longitude": float(pg.longitude),
            "price": pg.price,
            "gender_type": pg.gender_type,
            "rating": float(pg.rating),
            "area": pg.area,
            "city": pg.city,
            "distance_km": round(dist / 1000, 2) if dist else None,
        })
    return results


def update_rating(db: Session, pg_id: int) -> None:
    from app.models.review import Review
    result = db.execute(
        select(func.avg(Review.rating), func.count(Review.id))
        .where(Review.pg_id == pg_id)
    ).first()
    avg_rating, count = result
    pg = db.get(PGListing, pg_id)
    if pg:
        pg.rating = round(float(avg_rating or 0), 2)
        pg.total_reviews = count or 0
        db.commit()
