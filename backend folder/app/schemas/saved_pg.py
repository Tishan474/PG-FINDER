from pydantic import BaseModel
from datetime import datetime
from app.schemas.pg_listing import PGListingResponse


class SavedPGResponse(BaseModel):
    id: int
    pg_id: int
    saved_at: datetime
    pg: PGListingResponse

    model_config = {"from_attributes": True}
