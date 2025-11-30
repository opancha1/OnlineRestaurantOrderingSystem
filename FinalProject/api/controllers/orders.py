from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status, Response
from sqlalchemy.exc import SQLAlchemyError
from ..models import order as model
from ..models import menu_item as menu_model
from ..models import order_details as order_detail_model
from uuid import uuid4


def create(db: Session, request):
    new_item = model.Order(
        status=request.status or "Pending",
        total_price=request.total_price,
        tracking_number=request.tracking_number,
        user_id=request.user_id,
    )

    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
    except SQLAlchemyError as e:
        error = str(e.__dict__["orig"])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return new_item


def read_all(db: Session):
    try:
        result = (
            db.query(model.Order)
            .options(joinedload(model.Order.order_details))
            .all()
        )
    except SQLAlchemyError as e:
        error = str(e.__dict__["orig"])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return result


def read_one(db: Session, item_id):
    try:
        item = (
            db.query(model.Order)
            .options(joinedload(model.Order.order_details))
            .filter(model.Order.id == item_id)
            .first()
        )
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
    except SQLAlchemyError as e:
        error = str(e.__dict__["orig"])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item


def update(db: Session, item_id, request):
    try:
        item = db.query(model.Order).filter(model.Order.id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        update_data = request.dict(exclude_unset=True)
        item.update(update_data, synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__["orig"])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item.first()


def delete(db: Session, item_id):
    try:
        item = db.query(model.Order).filter(model.Order.id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        item.delete(synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__["orig"])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def create_guest_order(db: Session, request):
    if not request.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one menu item.",
        )

    menu_item_ids = [item.menu_item_id for item in request.items]

    # Fetch menu items in a single query
    existing_items = (
        db.query(menu_model.MenuItem)
        .filter(menu_model.MenuItem.id.in_(menu_item_ids))
        .all()
    )
    existing_item_map = {item.id: item for item in existing_items}

    missing_items = sorted(set(menu_item_ids) - set(existing_item_map.keys()))
    if missing_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Menu items not found: {missing_items}",
        )

    total_price = 0.0
    order_details = []
    for item in request.items:
        menu_item_obj = existing_item_map[item.menu_item_id]
        total_price += float(menu_item_obj.price) * item.quantity
        order_details.append(
            order_detail_model.OrderDetail(
                menu_item_id=item.menu_item_id,
                quantity=item.quantity,
            )
        )

    new_order = model.Order(
        status="Pending",
        total_price=total_price,
        tracking_number=str(uuid4()),
        guest_name=request.guest_name,
        guest_email=request.guest_email,
        guest_phone=request.guest_phone,
        order_details=order_details,
    )

    try:
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__["orig"])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return new_order
