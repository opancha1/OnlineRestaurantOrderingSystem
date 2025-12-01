from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from ..models import review as review_model
from ..models import user as user_model
from ..models import menu_item as menu_model
from ..schemas import review as review_schema


def create(db: Session, request: review_schema.ReviewCreate):
    # Ensure user and menu item exist
    if not db.query(user_model.User.id).filter(user_model.User.id == request.user_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if not db.query(menu_model.MenuItem.id).filter(menu_model.MenuItem.id == request.menu_item_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found.")
    new_item = review_model.Review(
        user_id=request.user_id,
        menu_item_id=request.menu_item_id,
        rating=request.rating,
        comment=request.comment,
    )
    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return new_item


def read_all(db: Session):
    try:
        return db.query(review_model.Review).all()
    except SQLAlchemyError as e:
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


def read_one(db: Session, item_id: int):
    try:
        review = db.query(review_model.Review).filter(review_model.Review.id == item_id).first()
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")
        return review
    except SQLAlchemyError as e:
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


def update(db: Session, item_id: int, request: review_schema.ReviewUpdate):
    review = db.query(review_model.Review).filter(review_model.Review.id == item_id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")

    update_data = request.model_dump(exclude_unset=True)
    if not update_data:
        return review

    try:
        for field, value in update_data.items():
            setattr(review, field, value)
        db.commit()
        db.refresh(review)
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return review


def delete(db: Session, item_id: int):
    review = db.query(review_model.Review).filter(review_model.Review.id == item_id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")
    try:
        db.delete(review)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return {"detail": "Review deleted"}
