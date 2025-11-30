from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from ..models import notification as notification_model
from ..models import order as order_model


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
