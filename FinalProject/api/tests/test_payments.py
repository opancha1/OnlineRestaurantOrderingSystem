import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..controllers import payments as payments_controller
from ..controllers import orders as orders_controller
from ..dependencies.database import Base
from ..models import menu_item as menu_model
from ..models import user as user_model
from ..models import order_details as order_details_model  # register relationship metadata
from ..models import payment as payment_model  # register relationship metadata
from ..models import review as review_model  # register relationship metadata
from ..schemas import payment as payment_schema
from ..schemas import order as order_schema


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_order_with_items(db_session):
    user = user_model.User(
        name="Payment User",
        email="payuser@example.com",
        phone="555",
        address="123 Pay St",
        password="hashed",
        role="customer",
    )
    item = menu_model.MenuItem(name="Combo Meal", description="Burger and fries", price=15.0, category="entree", calories=900)
    db_session.add_all([user, item])
    db_session.commit()

    order_request = order_schema.OrderCreate(
        user_id=user.id,
        items=[order_schema.OrderItem(menu_item_id=item.id, quantity=2)],
    )
    return orders_controller.create(db_session, order_request)


def test_create_payment_success(db_session):
    order = create_order_with_items(db_session)
    payment_request = payment_schema.PaymentCreate(
        order_id=order.id,
        payment_type="Card",
        transaction_status="Success",
        amount=order.total_price,
    )

    payment = payments_controller.create(db_session, payment_request)

    assert payment.id is not None
    assert payment.order_id == order.id
    assert payment.amount == pytest.approx(order.total_price)


def test_create_payment_amount_mismatch(db_session):
    order = create_order_with_items(db_session)
    payment_request = payment_schema.PaymentCreate(
        order_id=order.id,
        payment_type="Cash",
        transaction_status="Pending",
        amount=order.total_price + 5,
    )

    with pytest.raises(HTTPException) as exc:
        payments_controller.create(db_session, payment_request)

    assert "must match the order total" in str(exc.value.detail)


def test_read_payment_by_id(db_session):
    order = create_order_with_items(db_session)
    payment = payments_controller.create(
        db_session,
        payment_schema.PaymentCreate(
            order_id=order.id,
            payment_type="UPI",
            transaction_status="Success",
            amount=order.total_price,
        ),
    )

    fetched = payments_controller.read_one(db_session, payment.id)

    assert fetched.id == payment.id
    assert fetched.payment_type == "UPI"
