from fastapi import APIRouter, Depends, status, Query
from sqlmodel import Session, select, func
from model import Review, ReviewRead, ReviewCreate, ReviewUpdate, AverageReview
from database import get_session
from exceptions import InvalidPlayNameError, InvalidReviewIdError

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
def create_review(review: ReviewCreate, session: Session = Depends(get_session)) -> ReviewRead:
    db_review = Review.model_validate(review) # Review(**review.model_dump()) old method
    session.add(db_review)
    session.commit()
    session.refresh(db_review)
    return db_review


@router.get(
    "/",
    response_model= list[ReviewRead],
    status_code= status.HTTP_200_OK
    )
def list_reviews(
    play_name: str | None = Query(None, description="Filter by play_name"),
    skip: int = Query(0, ge=0, description="Number of reviews to skip"),
    limit: int = Query(10, ge=0, le=50, description="Number of reviews to return"),
    session: Session = Depends(get_session)
    ) -> list[ReviewRead]:
    querry = select(Review)
    
    if play_name:
        querry = querry.where(Review.play_name == play_name)
    
    querry = querry.offset(skip).limit(limit) # pagination using offset and limit.
    reviews = session.exec(querry).all()
    return reviews
    

@router.get(
    "/average/{play_name}",
    response_model= AverageReview,
    status_code= status.HTTP_200_OK
)
def get_average_rating(
    play_name: str,
    session: Session = Depends(get_session)
) -> AverageReview:
    result = session.exec(
        select(
            func.avg(Review.rating).label("average_rating"),
            func.count(Review.id).label("total_reviews")
        )
        .where(Review.play_name == play_name)
    ).first()
    
    avg_rating, total_reviews = result
    
    if total_reviews == 0:
        raise InvalidPlayNameError(play_name)
    
    return AverageReview(
        play_name = play_name,
        average_rating = avg_rating,
        total_reviews = total_reviews
    )
    

@router.get(
    "/{id}",
    response_model= ReviewRead,
    status_code= status.HTTP_200_OK
)
def get_review_for_id(
    id: int,
    session: Session = Depends(get_session)
) -> ReviewRead:
    review = session.get(Review, id)
    
    if not review:
        raise InvalidReviewIdError(id)
    
    return review


@router.patch(
    "/{id}",
    response_model=ReviewRead,
    status_code=status.HTTP_200_OK,
)
def update_review_for_id(
    id: int,
    update: ReviewUpdate,
    session: Session = Depends(get_session),
) -> ReviewRead:
    review = session.get(Review, id)

    if review is None:
        raise InvalidReviewIdError(id)

    update_data = update.model_dump(exclude_unset=True)

    review.sqlmodel_update(update_data)

    session.add(review)
    session.commit()
    session.refresh(review)

    return review


@router.delete(
    "/{id}",
    status_code= status.HTTP_200_OK
)
def delete_review_for_id(
    id: int,
    session: Session = Depends(get_session)
) -> dict[str, str]:
    review = session.get(Review, id)
    
    if review is None:
        raise InvalidReviewIdError(id)
    
    
    session.delete(review)
    session.commit()
    
    
    return {
        "status": "success",
        "message": "Review deleted successfully"
    }