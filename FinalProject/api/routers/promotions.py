from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..controllers import promotions as controller
from ..schemas import promotion as schema
from ..dependencies.database import get_db

router = APIRouter(tags=["Promotions"], prefix="/promotions")


@router.post("/", response_model=schema.PromotionResponse, status_code=status.HTTP_201_CREATED)
def create_promotion(request: schema.PromotionCreate, db: Session = Depends(get_db)):
    return controller.create(db=db, request=request)


@router.get("/", response_model=list[schema.PromotionResponse])
def list_promotions(db: Session = Depends(get_db)):
    return controller.read_all(db=db)
