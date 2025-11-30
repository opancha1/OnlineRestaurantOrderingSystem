from fastapi import HTTPException, status, Response
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

    if request.transaction_status.lower() == "success":
        order.status = "Paid"

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


def update(db: Session, item_id: int, request):
    payment = (
        db.query(payment_model.Payment)
        .filter(payment_model.Payment.id == item_id)
        .first()
    )
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found!"
        )

    order = db.query(order_model.Order).filter(order_model.Order.id == payment.order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found!")

    update_data = request.model_dump(exclude_unset=True)

    if "amount" in update_data:
        expected_total = float(order.total_price or 0)
        if round(update_data["amount"], 2) != round(expected_total, 2):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment amount must match the order total.",
            )
        payment.amount = update_data["amount"]

    if "payment_type" in update_data:
        payment.payment_type = update_data["payment_type"]

    if "transaction_status" in update_data:
        payment.transaction_status = update_data["transaction_status"]
        if update_data["transaction_status"] and update_data["transaction_status"].lower() == "success":
            order.status = "Paid"
        else:
            order.status = "Pending"

    try:
        db.commit()
        db.refresh(payment)
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return payment


def delete(db: Session, item_id: int):
    payment = (
        db.query(payment_model.Payment)
        .filter(payment_model.Payment.id == item_id)
        .first()
    )
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found!"
        )

    order = db.query(order_model.Order).filter(order_model.Order.id == payment.order_id).first()

    try:
        db.delete(payment)
        if order:
            order.status = "Pending"
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
