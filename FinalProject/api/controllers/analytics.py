from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from ..models import order as order_model
from ..models import order_details as order_detail_model
from ..models import menu_item as menu_item_model


def sales_summary(db: Session):
    try:
        total_revenue = db.query(func.coalesce(func.sum(order_model.Order.total_price), 0)).scalar() or 0
        total_orders = db.query(func.count(order_model.Order.id)).scalar() or 0
        return {"total_orders": int(total_orders), "total_revenue": float(total_revenue)}
    except SQLAlchemyError as e:
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


def popular_items(db: Session, limit: int = 10):
    try:
        rows = (
            db.query(
                order_detail_model.OrderDetail.menu_item_id.label("menu_item_id"),
                menu_item_model.MenuItem.name.label("name"),
                func.sum(order_detail_model.OrderDetail.quantity).label("total_quantity"),
                func.sum(order_detail_model.OrderDetail.quantity * menu_item_model.MenuItem.price).label("total_revenue"),
            )
            .join(menu_item_model.MenuItem, menu_item_model.MenuItem.id == order_detail_model.OrderDetail.menu_item_id)
            .group_by(order_detail_model.OrderDetail.menu_item_id, menu_item_model.MenuItem.name)
            .order_by(func.sum(order_detail_model.OrderDetail.quantity).desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "menu_item_id": r.menu_item_id,
                "name": r.name,
                "total_quantity": int(r.total_quantity or 0),
                "total_revenue": float(r.total_revenue or 0),
            }
            for r in rows
        ]
    except SQLAlchemyError as e:
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
