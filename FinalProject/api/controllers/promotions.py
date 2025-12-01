from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from ..models import promotion as promotion_model


def create(db: Session, request):
    promo_code = request.promo_code.upper()

    existing = (
        db.query(promotion_model.Promotion)
        .filter(promotion_model.Promotion.promo_code == promo_code)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Promo code already exists.",
        )

    new_item = promotion_model.Promotion(
        promo_code=promo_code,
        discount_percent=request.discount_percent,
        expiration_date=request.expiration_date,
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
        return db.query(promotion_model.Promotion).all()
    except SQLAlchemyError as e:
        error = str(e.__dict__["orig"])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


def read_one(db: Session, item_id: int):
    try:
        promo = (
            db.query(promotion_model.Promotion)
            .filter(promotion_model.Promotion.id == item_id)
            .first()
        )
        if not promo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promotion not found.")
        return promo
    except SQLAlchemyError as e:
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


def update(db: Session, item_id: int, request):
    promo = (
        db.query(promotion_model.Promotion)
        .filter(promotion_model.Promotion.id == item_id)
        .first()
    )
    if not promo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promotion not found.")

    update_data = request.model_dump(exclude_unset=True)
    if "promo_code" in update_data and update_data["promo_code"]:
        update_data["promo_code"] = update_data["promo_code"].upper()

    if not update_data:
        return promo

    if "promo_code" in update_data:
        existing = (
            db.query(promotion_model.Promotion)
            .filter(promotion_model.Promotion.promo_code == update_data["promo_code"])
            .filter(promotion_model.Promotion.id != item_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Promo code already exists.",
            )

    try:
        for field, value in update_data.items():
            setattr(promo, field, value)
        db.commit()
        db.refresh(promo)
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return promo


def delete(db: Session, item_id: int):
    promo = (
        db.query(promotion_model.Promotion)
        .filter(promotion_model.Promotion.id == item_id)
        .first()
    )
    if not promo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promotion not found.")

    try:
        db.delete(promo)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return {"detail": "Promotion deleted"}


def get_valid_promotion(db: Session, promo_code: str):
    if not promo_code:
        return None
    promo = (
        db.query(promotion_model.Promotion)
        .filter(promotion_model.Promotion.promo_code == promo_code.upper())
        .first()
    )
    if not promo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promo code not found.")
    if promo.expiration_date and promo.expiration_date < date.today():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Promo code expired.")
    return promo
