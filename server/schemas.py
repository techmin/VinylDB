from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VinylBase(BaseModel):
    title: str
    artist: str
    year: Optional[int] = None
    cat_no: Optional[str] = None
    genre: Optional[str] = None

class VinylCreate(VinylBase):
    pass

class VinylResponse(VinylBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
