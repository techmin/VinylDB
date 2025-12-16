from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .database import Base

class Vinyl(Base):
    __tablename__ = "vinyls"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    artist = Column(String, index=True)
    year = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Metadata fields (can be expanded later)
    cat_no = Column(String, nullable=True)
    genre = Column(String, nullable=True)
