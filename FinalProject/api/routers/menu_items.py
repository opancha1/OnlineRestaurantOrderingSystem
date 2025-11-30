from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..controllers import menu_items as controller
from ..schemas import menu_item as schema
from ..dependencies.database import get_db

router = APIRouter(tags=["Menu"], prefix="/menu")


@router.post("/", response_model=schema.MenuItemResponse, status_code=status.HTTP_201_CREATED)
def create_menu_item(request: schema.MenuItemCreate, db: Session = Depends(get_db)):
    return controller.create(db=db, request=request)


@router.get("/", response_model=list[schema.MenuItemResponse])
def read_menu(db: Session = Depends(get_db)):
    return controller.read_all(db)


@router.get("/filter", response_model=list[schema.MenuItemResponse])
def filter_menu(category: str | None = None, db: Session = Depends(get_db)):
    return controller.read_filtered(db, category=category)


@router.get("/{item_id}", response_model=schema.MenuItemResponse)
def read_menu_item(item_id: int, db: Session = Depends(get_db)):
    return controller.read_one(db, item_id=item_id)


@router.put("/{item_id}", response_model=schema.MenuItemResponse)
def update_menu_item(
    item_id: int, request: schema.MenuItemCreate, db: Session = Depends(get_db)
):
    return controller.update(db=db, item_id=item_id, request=request)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(item_id: int, db: Session = Depends(get_db)):
    return controller.delete(db=db, item_id=item_id)
