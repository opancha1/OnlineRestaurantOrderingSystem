from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..controllers import users as controller
from ..schemas import user as schema
from ..dependencies.database import get_db

router = APIRouter(tags=["Users"], prefix="/users")


@router.post("/", response_model=schema.UserResponse, status_code=201)
def create_user(request: schema.UserCreate, db: Session = Depends(get_db)):
    return controller.create(db=db, request=request)


@router.get("/", response_model=list[schema.UserResponse])
def read_users(db: Session = Depends(get_db)):
    return controller.read_all(db)


@router.get("/{id}", response_model=schema.UserResponse)
def read_user(id: int, db: Session = Depends(get_db)):
    return controller.read_one(db, item_id=id)


@router.put("/{id}", response_model=schema.UserResponse)
def update_user(id: int, request: schema.UserUpdate, db: Session = Depends(get_db)):
    return controller.update(db, item_id=id, request=request)


@router.delete("/{id}")
def delete_user(id: int, db: Session = Depends(get_db)):
    return controller.delete(db, item_id=id)
