from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..controllers import payments as controller
from ..schemas import payment as schema
from ..dependencies.database import get_db

router = APIRouter(tags=["Payments"], prefix="/payments")


@router.post("/", response_model=schema.PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(request: schema.PaymentCreate, db: Session = Depends(get_db)):
    return controller.create(db=db, request=request)


@router.get("/{payment_id}", response_model=schema.PaymentResponse)
def read_payment(payment_id: int, db: Session = Depends(get_db)):
    return controller.read_one(db=db, item_id=payment_id)
