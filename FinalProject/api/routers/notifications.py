from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..controllers import notifications as controller
from ..schemas import notification as schema
from ..dependencies.database import get_db

router = APIRouter(tags=["Notifications"], prefix="/notifications")


@router.post("/test", response_model=schema.NotificationResponse, status_code=status.HTTP_201_CREATED)
def send_test_notification(request: schema.NotificationCreate, db: Session = Depends(get_db)):
    return controller.send_test(db=db, message=request.message, order_id=request.order_id)
