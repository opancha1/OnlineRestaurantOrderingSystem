from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from ..models import payment as payment_model
from ..models import order as order_model


def create(db: Session, request):
    order = db.query(order_model.Order).filter(order_model.Order.id == request.order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found!")

    # Disallow duplicate payments for the same order.
    existing_payment = (
        db.query(payment_model.Payment)
        .filter(payment_model.Payment.order_id == request.order_id)
        .first()
    )
    if existing_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment already exists for this order.",
        )

    expected_total = float(order.total_price or 0)
    if round(request.amount, 2) != round(expected_total, 2):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount must match the order total.",
        )

    new_payment = payment_model.Payment(
        order_id=request.order_id,
        payment_type=request.payment_type,
        transaction_status=request.transaction_status,
        amount=request.amount,
    )

    try:
        db.add(new_payment)
        db.commit()
        db.refresh(new_payment)
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return new_payment


def read_one(db: Session, item_id: int):
    try:
        payment = (
            db.query(payment_model.Payment)
            .filter(payment_model.Payment.id == item_id)
            .first()
        )
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found!"
            )
    except SQLAlchemyError as e:
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return payment
