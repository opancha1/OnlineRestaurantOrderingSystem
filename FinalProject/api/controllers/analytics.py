from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from ..models import order as order_model
from ..models import order_details as order_detail_model
from ..models import menu_item as menu_item_model
from ..models import review as review_model


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


def sales_by_date_range(db: Session, start_date: str | None, end_date: str | None):
    filters = []
    if start_date:
        filters.append(func.date(order_model.Order.order_date) >= start_date)
    if end_date:
        filters.append(func.date(order_model.Order.order_date) <= end_date)
    try:
        query = db.query(
            func.coalesce(func.sum(order_model.Order.total_price), 0).label("revenue"),
            func.coalesce(func.count(order_model.Order.id), 0).label("order_count"),
        )
        if filters:
            query = query.filter(*filters)
        row = query.one()
        return {"total_orders": int(row.order_count or 0), "total_revenue": float(row.revenue or 0)}
    except SQLAlchemyError as e:
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


def low_rated_items(db: Session, max_rating: int = 2):
    try:
        rows = (
            db.query(
                menu_item_model.MenuItem.id.label("menu_item_id"),
                menu_item_model.MenuItem.name.label("name"),
                func.avg(order_model.Order.total_price).label("avg_order_total"),
                func.avg(menu_item_model.MenuItem.price).label("avg_price"),  # rough context
                func.avg(func.coalesce(review_model.Review.rating, 0)).label("avg_rating"),
                func.count(review_model.Review.id).label("review_count"),
            )
            .join(review_model.Review, review_model.Review.menu_item_id == menu_item_model.MenuItem.id)
            .group_by(menu_item_model.MenuItem.id, menu_item_model.MenuItem.name)
            .having(func.avg(review_model.Review.rating) <= max_rating)
            .order_by(func.avg(review_model.Review.rating).asc())
            .all()
        )
        return [
          {
            "menu_item_id": r.menu_item_id,
            "name": r.name,
            "avg_rating": float(r.avg_rating or 0),
            "review_count": int(r.review_count or 0),
          }
          for r in rows
        ]
    except SQLAlchemyError as e:
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
