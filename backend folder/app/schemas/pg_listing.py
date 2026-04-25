from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.pg_listing import GenderType


class AmenityBase(BaseModel):
    name: str


class AmenityCreate(AmenityBase):
    pass


class AmenityResponse(AmenityBase):
    id: int
    model_config = {"from_attributes": True}


class PGListingCreate(BaseModel):
    name: str
    description: Optional[str] = None
    area: str
    city: str
    latitude: float
    longitude: float
    price: Decimal
    gender_type: GenderType
    amenity_ids: List[int] = []

    @field_validator("latitude")
    @classmethod
    def validate_lat(cls, v: float) -> float:
        if not (-90 <= v <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_lng(cls, v: float) -> float:
        if not (-180 <= v <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Price must be positive")
        return v

    @field_validator("name", "area", "city")
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Field cannot be empty")
        return v


class PGListingUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    area: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    price: Optional[Decimal] = None
    gender_type: Optional[GenderType] = None
    amenity_ids: Optional[List[int]] = None

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v <= 0:
            raise ValueError("Price must be positive")
        return v


class PGListingResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    area: str
    city: str
    latitude: float
    longitude: float
    price: Decimal
    gender_type: GenderType
    rating: float
    total_reviews: int
    created_by: int
    created_at: datetime
    amenities: List[AmenityResponse] = []
    distance_km: Optional[float] = None

    model_config = {"from_attributes": True}


class PGListingFilters(BaseModel):
    search: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    gender_type: Optional[GenderType] = None
    amenity_ids: Optional[List[int]] = None
    city: Optional[str] = None
    area: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    radius_km: Optional[float] = None
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"
    page: int = 1
    page_size: int = 20

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v: Optional[str]) -> Optional[str]:
        allowed = {"price", "rating", "distance", "created_at"}
        if v and v not in allowed:
            raise ValueError(f"sort_by must be one of: {allowed}")
        return v

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in {"asc", "desc"}:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v

    @field_validator("page")
    @classmethod
    def validate_page(cls, v: int) -> int:
        if v < 1:
            raise ValueError("page must be >= 1")
        return v

    @model_validator(mode="after")
    def validate_distance_params(self):
        if self.radius_km and (self.lat is None or self.lng is None):
            raise ValueError("lat and lng are required when radius_km is set")
        return self


class MapPGResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    price: Decimal
    gender_type: GenderType
    rating: float
    area: str
    city: str
    distance_km: Optional[float] = None

    model_config = {"from_attributes": True}
