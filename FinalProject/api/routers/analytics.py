from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..controllers import analytics as controller
from ..dependencies.database import get_db

router = APIRouter(tags=["Analytics"], prefix="/analytics")


@router.get("/sales")
def sales(db: Session = Depends(get_db)):
    return controller.sales_summary(db)


@router.get("/popular-items")
def popular_items(limit: int = 10, db: Session = Depends(get_db)):
    return controller.popular_items(db, limit=limit)


@router.get("/sales-range")
def sales_range(start_date: str | None = None, end_date: str | None = None, db: Session = Depends(get_db)):
    return controller.sales_by_date_range(db=db, start_date=start_date, end_date=end_date)


@router.get("/low-rated")
def low_rated(max_rating: int = 2, db: Session = Depends(get_db)):
    return controller.low_rated_items(db=db, max_rating=max_rating)
