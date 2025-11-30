from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response
from sqlalchemy.exc import SQLAlchemyError
from ..models import menu_item as model


def create(db: Session, request):
    new_item = model.MenuItem(
        name=request.name,
        description=request.description,
        price=request.price,
        category=request.category,
        calories=request.calories,
    )
    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return new_item


def read_all(db: Session):
    try:
        return db.query(model.MenuItem).all()
    except SQLAlchemyError as e:
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


def read_one(db: Session, item_id: int):
    try:
        item = db.query(model.MenuItem).filter(model.MenuItem.id == item_id).first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!"
            )
        return item
    except SQLAlchemyError as e:
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


def update(db: Session, item_id: int, request):
    try:
        item_q = db.query(model.MenuItem).filter(model.MenuItem.id == item_id)
        if not item_q.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!"
            )
        update_data = request.dict(exclude_unset=True)
        item_q.update(update_data, synchronize_session=False)
        db.commit()
        return item_q.first()
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


def delete(db: Session, item_id: int):
    try:
        item_q = db.query(model.MenuItem).filter(model.MenuItem.id == item_id)
        if not item_q.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!"
            )
        item_q.delete(synchronize_session=False)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
