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
