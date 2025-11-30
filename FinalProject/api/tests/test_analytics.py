import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..dependencies.database import Base
from ..controllers import analytics as analytics_controller
from ..controllers import orders as orders_controller
from ..models import menu_item as menu_model
from ..models import user as user_model
from ..models import order_details as order_details_model  # register metadata
from ..models import payment as payment_model  # register metadata
from ..models import notification as notification_model  # register metadata
from ..models import promotion as promotion_model  # register metadata
from ..models import review as review_model  # register metadata
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


def seed_orders(db_session):
    user = user_model.User(
        name="Analytics User",
        email="analytics@example.com",
        phone="123",
        address="Addr",
        password="hashed",
        role="customer",
    )
    pizza = menu_model.MenuItem(name="Pizza", description="Cheese", price=12.0)
    pasta = menu_model.MenuItem(name="Pasta", description="Red", price=9.0)
    db_session.add_all([user, pizza, pasta])
    db_session.commit()

    # Order 1: 2 pizza
    orders_controller.create(
        db_session,
        order_schema.OrderCreate(
            user_id=user.id,
            items=[order_schema.OrderItem(menu_item_id=pizza.id, quantity=2)],
        ),
    )
    # Order 2: 1 pizza, 3 pasta
    orders_controller.create(
        db_session,
        order_schema.OrderCreate(
            user_id=user.id,
            items=[
                order_schema.OrderItem(menu_item_id=pizza.id, quantity=1),
                order_schema.OrderItem(menu_item_id=pasta.id, quantity=3),
            ],
        ),
    )


def test_sales_summary(db_session):
    seed_orders(db_session)
    summary = analytics_controller.sales_summary(db_session)
    assert summary["total_orders"] == 2
    # total revenue: (2*12) + (1*12 + 3*9) = 24 + 39 = 63
    assert summary["total_revenue"] == pytest.approx(63.0)


def test_popular_items(db_session):
    seed_orders(db_session)
    popular = analytics_controller.popular_items(db_session)
    assert len(popular) == 2
    # Pasta sold 3, pizza sold 3, but pizza first order? tie order by sum desc maybe insertion: ensure counts
    quantities = {item["name"]: item["total_quantity"] for item in popular}
    assert quantities["Pizza"] == 3
    assert quantities["Pasta"] == 3
    revenues = {item["name"]: item["total_revenue"] for item in popular}
    assert revenues["Pizza"] == pytest.approx(36.0)
    assert revenues["Pasta"] == pytest.approx(27.0)
