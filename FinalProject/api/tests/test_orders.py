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
        guest_email="guest@example.com",
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


def test_create_guest_order_missing_menu_item(db_session):
    request = order_schema.GuestOrderCreate(
        guest_name="Walk-in Guest",
        items=[order_schema.OrderItem(menu_item_id=999, quantity=1)],
    )

    with pytest.raises(HTTPException) as exc:
        controller.create_guest_order(db_session, request)

    assert "Menu items not found" in str(exc.value.detail)
