from fastapi import APIRouter, Depends, FastAPI, status, Response
from sqlalchemy.orm import Session
from ..controllers import orders as controller
from ..schemas import order as order_schema
from ..dependencies.database import engine, get_db

router = APIRouter(
    tags=['Orders'],
    prefix="/orders"
)


@router.post("/", response_model=order_schema.OrderResponse, status_code=status.HTTP_201_CREATED)
def create(request: order_schema.OrderCreate, db: Session = Depends(get_db)):
    return controller.create(db=db, request=request)


@router.post(
    "/guest",
    response_model=order_schema.OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_guest_order(
    request: order_schema.GuestOrderCreate, db: Session = Depends(get_db)
):
    return controller.create_guest_order(db=db, request=request)


@router.get("/", response_model=list[order_schema.OrderResponse])
def read_all(
    user_id: int | None = None,
    db: Session = Depends(get_db),
):
    return controller.read_all(db, user_id=user_id)


@router.get("/{item_id}", response_model=order_schema.OrderResponse)
def read_one(item_id: int, db: Session = Depends(get_db)):
    return controller.read_one(db, item_id=item_id)


@router.get("/track/{tracking_number}", response_model=order_schema.OrderResponse)
def track_order(tracking_number: str, db: Session = Depends(get_db)):
    return controller.track_by_number(db=db, tracking_number=tracking_number)


@router.get("/total/summary")
def total_price_for_user(user_id: int, db: Session = Depends(get_db)):
    return controller.total_price_for_user(db, user_id=user_id)


@router.put("/{item_id}", response_model=order_schema.OrderResponse)
def update(item_id: int, request: order_schema.OrderBase, db: Session = Depends(get_db)):
    return controller.update(db=db, request=request, item_id=item_id)


@router.delete("/{item_id}")
def delete(item_id: int, db: Session = Depends(get_db)):
    return controller.delete(db=db, item_id=item_id)
