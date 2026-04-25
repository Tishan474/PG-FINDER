from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    pg_id: int
    rating: float
    comment: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: float) -> float:
        if not (1 <= v <= 5):
            raise ValueError("Rating must be between 1 and 5")
        return round(v * 2) / 2  # Round to nearest 0.5


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    pg_id: int
    rating: float
    comment: Optional[str]
    created_at: datetime
    user_name: Optional[str] = None

    model_config = {"from_attributes": True}
