from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..controllers import reviews as controller
from ..schemas import review as schema
from ..dependencies.database import get_db

router = APIRouter(tags=["Reviews"], prefix="/reviews")


@router.post("/", response_model=schema.ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(request: schema.ReviewCreate, db: Session = Depends(get_db)):
    return controller.create(db=db, request=request)


@router.get("/", response_model=list[schema.ReviewResponse])
def list_reviews(db: Session = Depends(get_db)):
    return controller.read_all(db=db)


@router.get("/{id}", response_model=schema.ReviewResponse)
def read_review(id: int, db: Session = Depends(get_db)):
    return controller.read_one(db=db, item_id=id)


@router.put("/{id}", response_model=schema.ReviewResponse)
def update_review(id: int, request: schema.ReviewUpdate, db: Session = Depends(get_db)):
    return controller.update(db=db, item_id=id, request=request)


@router.delete("/{id}")
def delete_review(id: int, db: Session = Depends(get_db)):
    return controller.delete(db=db, item_id=id)
