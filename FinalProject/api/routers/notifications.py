from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..controllers import notifications as controller
from ..schemas import notification as schema
from ..dependencies.database import get_db

router = APIRouter(tags=["Notifications"], prefix="/notifications")


@router.post("/test", response_model=schema.NotificationResponse, status_code=status.HTTP_201_CREATED)
def send_test_notification(request: schema.NotificationCreate, db: Session = Depends(get_db)):
    return controller.send_test(db=db, message=request.message, order_id=request.order_id)


@router.get("/", response_model=list[schema.NotificationResponse])
def list_notifications(db: Session = Depends(get_db)):
    return controller.read_all(db=db)


@router.get("/{id}", response_model=schema.NotificationResponse)
def read_notification(id: int, db: Session = Depends(get_db)):
    return controller.read_one(db=db, item_id=id)


@router.put("/{id}", response_model=schema.NotificationResponse)
def update_notification(id: int, request: schema.NotificationUpdate, db: Session = Depends(get_db)):
    return controller.update(db=db, item_id=id, request=request)


@router.delete("/{id}")
def delete_notification(id: int, db: Session = Depends(get_db)):
    return controller.delete(db=db, item_id=id)
