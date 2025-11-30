import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..controllers import orders as controller
from ..dependencies.database import Base
from ..models import menu_item as menu_model
from ..models import user as user_model  # ensure users table is registered
from ..models import order_details as order_details_model  # ensure order_details table is registered
from ..models import payment as payment_model  # ensure payment table is registered
from ..models import notification as notification_model  # ensure notification table is registered
from ..models import review as review_model  # ensure review table is registered
from ..schemas import order as order_schema


@pytest.fixture
def db_session():
    """Provide an isolated in-memory database session for each test."""
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_create_guest_order_success(db_session):
    # Seed menu items
    item1 = menu_model.MenuItem(name="Sandwich", description="Tasty", price=5.0)
    item2 = menu_model.MenuItem(name="Soup", description="Warm", price=3.0)
    db_session.add_all([item1, item2])
    db_session.commit()

    request = order_schema.GuestOrderCreate(
        guest_name="Walk-in Guest",
        items=[
            order_schema.OrderItem(menu_item_id=item1.id, quantity=2),
            order_schema.OrderItem(menu_item_id=item2.id, quantity=1),
        ],
    )

    created_order = controller.create_guest_order(db_session, request)

    assert created_order.id is not None
    assert created_order.guest_name == "Walk-in Guest"
    assert created_order.total_price == pytest.approx(13.0)
    assert len(created_order.order_details) == 2
    assert created_order.tracking_number is not None
    assert created_order.order_details[0].unit_price is not None
    assert created_order.order_details[0].line_total is not None


def test_create_guest_order_missing_menu_item(db_session):
    request = order_schema.GuestOrderCreate(
        guest_name="Walk-in Guest",
        items=[order_schema.OrderItem(menu_item_id=999, quantity=1)],
    )

    with pytest.raises(HTTPException) as exc:
        controller.create_guest_order(db_session, request)

    assert "Menu items not found" in str(exc.value.detail)


def test_create_user_order_with_multiple_items(db_session):
    # Seed user and menu items
    user = user_model.User(
        name="Test User",
        email="user@example.com",
        phone="123",
        address="123 Street",
        password="hashed",
        role="customer",
    )
    item1 = menu_model.MenuItem(name="Pasta", description="Cheesy", price=12.0)
    item2 = menu_model.MenuItem(name="Salad", description="Fresh", price=6.0)
    db_session.add_all([user, item1, item2])
    db_session.commit()

    request = order_schema.OrderCreate(
        user_id=user.id,
        items=[
            order_schema.OrderItem(menu_item_id=item1.id, quantity=1),
            order_schema.OrderItem(menu_item_id=item2.id, quantity=2),
        ],
    )

    created_order = controller.create(db_session, request)

    assert created_order.user_id == user.id
    assert created_order.total_price == pytest.approx(24.0)
    assert len(created_order.order_details) == 2


def test_filter_orders_by_user_id(db_session):
    # Seed users and menu items
    user1 = user_model.User(
        name="User One",
        email="one@example.com",
        phone="111",
        address="Addr1",
        password="hashed",
        role="customer",
    )
    user2 = user_model.User(
        name="User Two",
        email="two@example.com",
        phone="222",
        address="Addr2",
        password="hashed",
        role="customer",
    )
    item = menu_model.MenuItem(name="Pizza", description="Cheese", price=10.0)
    db_session.add_all([user1, user2, item])
    db_session.commit()

    controller.create(
        db_session,
        order_schema.OrderCreate(
            user_id=user1.id, items=[order_schema.OrderItem(menu_item_id=item.id, quantity=1)]
        ),
    )
    controller.create(
        db_session,
        order_schema.OrderCreate(
            user_id=user2.id, items=[order_schema.OrderItem(menu_item_id=item.id, quantity=2)]
        ),
    )

    user1_orders = controller.read_all(db_session, user_id=user1.id)
    assert len(user1_orders) == 1
    assert user1_orders[0].user_id == user1.id


def test_total_price_for_user(db_session):
    user = user_model.User(
        name="Totals User",
        email="totals@example.com",
        phone="333",
        address="Addr3",
        password="hashed",
        role="customer",
    )
    item = menu_model.MenuItem(name="Burger", description="Beefy", price=10.0)
    db_session.add_all([user, item])
    db_session.commit()

    controller.create(
        db_session,
        order_schema.OrderCreate(
            user_id=user.id, items=[order_schema.OrderItem(menu_item_id=item.id, quantity=1)]
        ),
    )
    controller.create(
        db_session,
        order_schema.OrderCreate(
            user_id=user.id, items=[order_schema.OrderItem(menu_item_id=item.id, quantity=2)]
        ),
    )

    summary = controller.total_price_for_user(db_session, user.id)
    assert summary["user_id"] == user.id
    assert summary["total_price"] == pytest.approx(30.0)


def test_track_order_by_tracking_number_registered_user(db_session):
    user = user_model.User(
        name="Track User",
        email="track@example.com",
        phone="000",
        address="Addr",
        password="hashed",
        role="customer",
    )
    item = menu_model.MenuItem(name="Wrap", description="Tasty", price=8.0)
    db_session.add_all([user, item])
    db_session.commit()

    created = controller.create(
        db_session,
        order_schema.OrderCreate(
            user_id=user.id, items=[order_schema.OrderItem(menu_item_id=item.id, quantity=1)]
        ),
    )

    tracked = controller.track_by_number(db_session, created.tracking_number)
    assert tracked.id == created.id
    assert tracked.user_id == user.id
    assert tracked.tracking_number == created.tracking_number


def test_track_order_by_tracking_number_guest(db_session):
    item = menu_model.MenuItem(name="Cookie", description="Sweet", price=2.5)
    db_session.add(item)
    db_session.commit()

    created = controller.create_guest_order(
        db_session,
        order_schema.GuestOrderCreate(
            guest_name="Guest Tracker",
            guest_phone="123",
            items=[order_schema.OrderItem(menu_item_id=item.id, quantity=3)],
        ),
    )

    tracked = controller.track_by_number(db_session, created.tracking_number)
    assert tracked.id == created.id
    assert tracked.guest_name == "Guest Tracker"
