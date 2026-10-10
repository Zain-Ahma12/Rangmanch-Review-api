from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone

class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    play_name: str = Field(index=True)  # this field is for indexing which means it will be used for searching
    reviewer_name: str
    rating: int = Field(ge=0, le=5)
    comment: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) # this will set the created_at field to the current UTC time
    )
    

class ReviewCreate(SQLModel):
    play_name: str
    reviewer_name: str
    rating: int = Field(ge=0, le=5)
    comment: str

class ReviewRead(SQLModel):
    id: int
    play_name: str
    reviewer_name: str
    rating: int
    comment: str
    created_at: datetime
    
class ReviewUpdate(SQLModel):
    rating: Optional[int] = Field(default=None, ge=0, le=5)
    comment: Optional[str]
    

class AverageReview(SQLModel):
    play_name: str
    average_rating: float
    total_reviews: int