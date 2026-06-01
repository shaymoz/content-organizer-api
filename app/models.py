from pydantic import BaseModel
from typing import List, Optional, Literal
from sqlalchemy import Column, Integer, String
from .database import Base

# Pydantic models for API
class URLInput(BaseModel):
    url: str

class ContentBase(BaseModel):
    title: str
    description: str
    thumbnail_url: str
    content_type: Literal['Recipe', 'Restaurant', 'Place']

class ContentCreate(ContentBase):
    ingredients: Optional[List[str]] = None
    steps: Optional[List[str]] = None
    name: Optional[str] = None
    address: Optional[str] = None
    google_maps_link: Optional[str] = None

class ContentResponse(ContentBase):
    id: int
    ingredients: Optional[List[str]] = None
    steps: Optional[List[str]] = None
    name: Optional[str] = None
    address: Optional[str] = None
    google_maps_link: Optional[str] = None

    class Config:
        from_attributes = True

# SQLAlchemy model
class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    title = Column(String)
    description = Column(String)
    thumbnail_url = Column(String)
    content_type = Column(String)  # Recipe, Restaurant, Place
    ingredients = Column(String)   # JSON string of list
    steps = Column(String)         # JSON string of list
    name = Column(String)
    address = Column(String)
    google_maps_link = Column(String)