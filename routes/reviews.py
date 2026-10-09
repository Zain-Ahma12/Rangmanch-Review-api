from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select, func
from model import Review, ReviewRead, ReviewCreate, ReviewUpdate
from database import get_session

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"]
)

# /reviews/
@router.post(
    "/",
    response_model= ReviewRead,
    status_code= status.HTTP_201_CREATED
    ) # when you post a request to create a new review you will get back a response that follow this schema
def create_review(review: ReviewCreate, session: Session = Depends(get_session)):
    db_review = Review.model_validate(review) # Review(**review.model_dump()) old method
    session.add(db_review)
    session.commit()
    session.refresh(db_review)
    return db_review