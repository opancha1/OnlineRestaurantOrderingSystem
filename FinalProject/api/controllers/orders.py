from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from fastapi import HTTPException, status, Response
from sqlalchemy.exc import SQLAlchemyError
from ..models import order as model
from ..models import menu_item as menu_model
from ..models import order_details as order_detail_model
from ..controllers import promotions as promotion_controller
from ..controllers import notifications as notification_controller
from uuid import uuid4


def create(db: Session, request):
    # Expect items for registered user checkout
    if not request.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one menu item.",
        )

    menu_item_ids = [item.menu_item_id for item in request.items]
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
    # Enforce stock availability using menu_item.stock
    for item in request.items:
        menu_item_obj = existing_item_map[item.menu_item_id]
        if menu_item_obj.stock is not None and menu_item_obj.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for item {menu_item_obj.name} (id {menu_item_obj.id}).",
            )

    for item in request.items:
        menu_item_obj = existing_item_map[item.menu_item_id]
        unit_price = float(menu_item_obj.price)
        line_total = unit_price * item.quantity
        total_price += line_total
        od = order_detail_model.OrderDetail(
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
        )
        od.menu_item = menu_item_obj
        od.unit_price = unit_price  # transient for response
        od.line_total = line_total
        order_details.append(od)
        if menu_item_obj.stock is not None:
            menu_item_obj.stock = max(0, menu_item_obj.stock - item.quantity)

    promotion = None
    if request.promo_code:
        promotion = promotion_controller.get_valid_promotion(db, request.promo_code)
        discount = (promotion.discount_percent or 0) / 100
        total_price = max(0.0, total_price * (1 - discount))

    new_item = model.Order(
        status="Pending",
        total_price=total_price,
        tracking_number=str(uuid4()),
        order_type=request.order_type or "takeout",
        user_id=request.user_id,
        order_details=order_details,
        promotion_id=promotion.id if promotion else None,
        promotion_code=promotion.promo_code if promotion else None,
        promotion_discount=promotion.discount_percent if promotion else 0,
    )

    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    _attach_line_totals(new_item)
    return new_item


def read_all(db: Session, user_id: int | None = None, start_date: str | None = None, end_date: str | None = None):
    try:
        result = (
            db.query(model.Order)
            .options(
                joinedload(model.Order.order_details).joinedload(order_detail_model.OrderDetail.menu_item),
                joinedload(model.Order.payment),
            )
        )
        if user_id is not None:
            result = result.filter(model.Order.user_id == user_id)
        if start_date:
            result = result.filter(func.date(model.Order.order_date) >= start_date)
        if end_date:
            result = result.filter(func.date(model.Order.order_date) <= end_date)
        result = result.all()
    except SQLAlchemyError as e:
        error = str(e.__dict__["orig"])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return result


def read_one(db: Session, item_id):
    try:
        item = (
            db.query(model.Order)
            .options(
                joinedload(model.Order.order_details).joinedload(order_detail_model.OrderDetail.menu_item),
                joinedload(model.Order.payment),
            )
            .filter(model.Order.id == item_id)
            .first()
        )
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
    except SQLAlchemyError as e:
        error = str(e.__dict__["orig"])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item


def track_by_number(db: Session, tracking_number: str):
    try:
        item = (
            db.query(model.Order)
            .options(
                joinedload(model.Order.order_details).joinedload(order_detail_model.OrderDetail.menu_item),
                joinedload(model.Order.payment),
            )
            .filter(model.Order.tracking_number == tracking_number)
            .first()
        )
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tracking number not found!"
            )
    except SQLAlchemyError as e:
        error = str(e.__dict__["orig"])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item


def track_by_tracking_and_name(db: Session, tracking_number: str, name: str | None = None):
    try:
        query = (
            db.query(model.Order)
            .options(
                joinedload(model.Order.order_details).joinedload(order_detail_model.OrderDetail.menu_item),
                joinedload(model.Order.payment),
            )
            .filter(model.Order.tracking_number == tracking_number)
        )
        if name:
            lowered = name.strip().lower()
            query = query.filter(
                func.lower(model.Order.guest_name) == lowered
            )
        item = query.first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tracking number (and name, if provided) not found!",
            )
    except SQLAlchemyError as e:
        error = str(e.__dict__["orig"])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item


def update_guest_details(db: Session, item_id: int, request):
    # Only allow updating guest contact info on guest orders (no user_id)
    order_obj = (
        db.query(model.Order)
        .filter(model.Order.id == item_id)
        .filter(model.Order.user_id.is_(None))
        .first()
    )
    if not order_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Guest order not found!"
        )

    update_data = request.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide guest_name, guest_email, guest_phone, description, or order_type to update.",
        )

    if "guest_name" in update_data:
        order_obj.guest_name = update_data["guest_name"]
    if "guest_phone" in update_data:
        order_obj.guest_phone = update_data["guest_phone"]
    if "guest_email" in update_data:
        order_obj.guest_email = update_data["guest_email"]
    if "description" in update_data:
        order_obj.description = update_data["description"]
    if "order_type" in update_data and update_data["order_type"]:
        order_obj.order_type = update_data["order_type"]

    try:
        db.commit()
        db.refresh(order_obj)
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return order_obj


def update(db: Session, item_id, request):
    try:
        item = db.query(model.Order).filter(model.Order.id == item_id)
        existing = item.first()
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        update_data = request.model_dump(exclude_unset=True)
        status_changed = "status" in update_data and update_data["status"] != existing.status
        item.update(update_data, synchronize_session=False)
        db.commit()
        updated = item.first()
        if status_changed:
            try:
                notification_controller.log_status_notification(
                    db=db, order_id=updated.id, new_status=updated.status
                )
            except HTTPException:
                # Notification failure shouldn't break order update
                pass
    except SQLAlchemyError as e:
        error = str(e.__dict__["orig"])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return updated


def delete(db: Session, item_id):
    try:
        order_obj = (
            db.query(model.Order)
            .options(
                joinedload(model.Order.order_details),
                joinedload(model.Order.payment),
            )
            .filter(model.Order.id == item_id)
            .first()
        )
        if not order_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")

        # Use ORM delete so cascades (order_details, payment) are honored by DB constraints.
        db.delete(order_obj)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__["orig"])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def total_price_for_user(db: Session, user_id: int):
    try:
        total = db.query(func.coalesce(func.sum(model.Order.total_price), 0)).filter(model.Order.user_id == user_id).scalar()
        return {"user_id": user_id, "total_price": float(total or 0)}
    except SQLAlchemyError as e:
        error = str(e.__dict__["orig"])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


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
        if menu_item_obj.stock is not None and menu_item_obj.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for item {menu_item_obj.name} (id {menu_item_obj.id}).",
            )

    for item in request.items:
        menu_item_obj = existing_item_map[item.menu_item_id]
        unit_price = float(menu_item_obj.price)
        line_total = unit_price * item.quantity
        total_price += line_total
        od = order_detail_model.OrderDetail(
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
        )
        od.menu_item = menu_item_obj
        od.unit_price = unit_price  # transient for response
        od.line_total = line_total
        order_details.append(od)
        if menu_item_obj.stock is not None:
            menu_item_obj.stock = max(0, menu_item_obj.stock - item.quantity)

    promotion = None
    if request.promo_code:
        promotion = promotion_controller.get_valid_promotion(db, request.promo_code)
        discount = (promotion.discount_percent or 0) / 100
        total_price = max(0.0, total_price * (1 - discount))

    new_order = model.Order(
        status="Pending",
        total_price=total_price,
        tracking_number=str(uuid4()),
        guest_name=request.guest_name,
        guest_email=request.guest_email,
        guest_phone=request.guest_phone,
        order_type=request.order_type or "takeout",
        description=request.description,
        order_details=order_details,
        promotion_id=promotion.id if promotion else None,
        promotion_code=promotion.promo_code if promotion else None,
        promotion_discount=promotion.discount_percent if promotion else 0,
    )

    try:
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__["orig"])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    _attach_line_totals(new_order)
    return new_order


def _attach_line_totals(order_obj):
    """Populate transient unit_price and line_total for response rendering."""
    for od in order_obj.order_details:
        if hasattr(od, "menu_item") and od.menu_item:
            unit_price = float(od.menu_item.price)
            od.unit_price = unit_price
            od.line_total = unit_price * od.quantity
