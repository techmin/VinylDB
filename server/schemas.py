from pydantic import BaseModel
from typing import Optional, List, Dict, Any
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


# Analytics Schemas
class RecentAddition(BaseModel):
    id: int
    title: str
    artist: str
    year: Optional[int]
    added_at: Optional[str]

class YearRange(BaseModel):
    oldest: Optional[int]
    newest: Optional[int]

class CollectionOverview(BaseModel):
    total_vinyls: int
    total_artists: int
    total_genres: int
    year_range: YearRange
    recent_additions: List[RecentAddition]

class DistributionItem(BaseModel):
    artist: Optional[str] = None
    genre: Optional[str] = None
    decade: Optional[str] = None
    count: int

class TimelineItem(BaseModel):
    month: Optional[str]
    added: int
    total: int

class SearchAnalytics(BaseModel):
    total_matches: int
    matches_by_field: Dict[str, int]

class AnalyticsDashboard(BaseModel):
    overview: Dict[str, Any]
    top_artists: List[Dict[str, Any]]
    genre_distribution: List[Dict[str, Any]]
    year_distribution: List[Dict[str, Any]]
    collection_timeline: List[Dict[str, Any]]
    generated_at: str
