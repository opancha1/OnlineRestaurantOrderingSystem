from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from ..models import notification as notification_model
from ..models import order as order_model
from ..schemas import notification as notification_schema


def create(db: Session, order_id: int | None, message: str, channel: str = "mock", notif_status: str = "sent"):
    if order_id is not None:
        order_exists = db.query(order_model.Order.id).filter(order_model.Order.id == order_id).first()
        if not order_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found for notification.")

    new_item = notification_model.Notification(
        order_id=order_id,
        message=message,
        channel=channel,
        status=notif_status,
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


def send_test(db: Session, message: str = "Test notification", order_id: int | None = None):
    return create(db, order_id=order_id, message=message)


def log_status_notification(db: Session, order_id: int, new_status: str):
    message = f"Order {order_id} status updated to {new_status}"
    return create(db, order_id=order_id, message=message)


def read_all(db: Session):
    try:
        return db.query(notification_model.Notification).all()
    except SQLAlchemyError as e:
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


def read_one(db: Session, item_id: int):
    try:
        notif = (
            db.query(notification_model.Notification)
            .filter(notification_model.Notification.id == item_id)
            .first()
        )
        if not notif:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
        return notif
    except SQLAlchemyError as e:
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


def update(db: Session, item_id: int, request: notification_schema.NotificationUpdate):
    notif = (
        db.query(notification_model.Notification)
        .filter(notification_model.Notification.id == item_id)
        .first()
    )
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")

    update_data = request.model_dump(exclude_unset=True)
    if not update_data:
        return notif

    if "order_id" in update_data and update_data["order_id"] is not None:
        order_exists = (
            db.query(order_model.Order.id)
            .filter(order_model.Order.id == update_data["order_id"])
            .first()
        )
        if not order_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found for notification.")

    try:
        for field, value in update_data.items():
            setattr(notif, field, value)
        db.commit()
        db.refresh(notif)
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return notif


def delete(db: Session, item_id: int):
    notif = (
        db.query(notification_model.Notification)
        .filter(notification_model.Notification.id == item_id)
        .first()
    )
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")

    try:
        db.delete(notif)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return {"detail": "Notification deleted"}
