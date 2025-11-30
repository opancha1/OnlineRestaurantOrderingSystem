import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..dependencies.database import Base
from ..controllers import notifications as notifications_controller
from ..controllers import orders as orders_controller
from ..controllers import payments as payments_controller
from ..models import menu_item as menu_model
from ..models import user as user_model
from ..models import order_details as order_details_model  # register
from ..models import payment as payment_model  # register
from ..models import notification as notification_model
from ..models import review as review_model  # register
from ..schemas import order as order_schema
from ..schemas import payment as payment_schema
from ..schemas import notification as notification_schema


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


def seed_order(db_session):
    item = menu_model.MenuItem(name="Notify Burger", description="Yum", price=10.0)
    db_session.add(item)
    db_session.commit()

    order = orders_controller.create_guest_order(
        db_session,
        order_schema.GuestOrderCreate(
            guest_name="Notify Guest",
            items=[order_schema.OrderItem(menu_item_id=item.id, quantity=1)],
        ),
    )
    return order


def test_send_test_notification(db_session):
    order = seed_order(db_session)
    created = notifications_controller.send_test(db_session, message="Hello", order_id=order.id)
    assert created.id is not None
    assert created.message == "Hello"
    assert created.order_id == order.id


def test_order_status_update_logs_notification(db_session):
    order = seed_order(db_session)

    orders_controller.update(
        db_session, order.id, order_schema.OrderBase(status="Ready")
    )

    count = db_session.query(notification_model.Notification).count()
    assert count == 1
    notif = db_session.query(notification_model.Notification).first()
    assert "Ready" in notif.message


def test_payment_success_logs_notification(db_session):
    user = user_model.User(
        name="Pay Notifier",
        email="notify@example.com",
        phone="555",
        address="Addr",
        password="hashed",
        role="customer",
    )
    item = menu_model.MenuItem(name="Combo", description="Meal", price=12.0)
    db_session.add_all([user, item])
    db_session.commit()
    order = orders_controller.create(
        db_session,
        order_schema.OrderCreate(
            user_id=user.id,
            items=[order_schema.OrderItem(menu_item_id=item.id, quantity=1)],
        ),
    )

    payments_controller.create(
        db_session,
        payment_schema.PaymentCreate(
            order_id=order.id,
            payment_type="Card",
            transaction_status="Success",
            amount=order.total_price,
        ),
    )

    notif = db_session.query(notification_model.Notification).first()
    assert notif is not None
    assert "Paid" in notif.message
