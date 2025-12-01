from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..controllers import users as controller
from ..schemas import user as schema
from ..dependencies.database import get_db

router = APIRouter(tags=["Users"], prefix="/users")


@router.get("/", response_model=list[schema.UserResponse])
def read_users(db: Session = Depends(get_db)):
    return controller.read_all(db)


@router.get("/{user_id}", response_model=schema.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    return controller.read_one(db, item_id=user_id)
