from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from ..models import user as user_model
from ..schemas import user as user_schema


def read_all(db: Session):
    try:
        return db.query(user_model.User).all()
    except SQLAlchemyError as e:
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


def read_one(db: Session, item_id: int):
    try:
        user = db.query(user_model.User).filter(user_model.User.id == item_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")
        return user
    except SQLAlchemyError as e:
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


def create(db: Session, request: user_schema.UserCreate):
    # Enforce unique email
    existing = (
        db.query(user_model.User)
        .filter(user_model.User.email == request.email)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )
    new_user = user_model.User(
        name=request.name,
        email=request.email,
        phone=request.phone,
        address=request.address,
        password=request.password,
        role=request.role,
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return new_user


def update(db: Session, item_id: int, request: user_schema.UserUpdate):
    user = db.query(user_model.User).filter(user_model.User.id == item_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    try:
        db.commit()
        db.refresh(user)
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return user


def delete(db: Session, item_id: int):
    user = db.query(user_model.User).filter(user_model.User.id == item_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")

    try:
        db.delete(user)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return {"detail": "User deleted"}
