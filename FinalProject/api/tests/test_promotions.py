import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..dependencies.database import Base
from ..controllers import promotions as promotions_controller
from ..controllers import orders as orders_controller
from ..models import promotion as promotion_model  # register metadata
from ..models import menu_item as menu_model
from ..models import user as user_model
from ..models import order_details as order_details_model  # register metadata
from ..models import payment as payment_model  # register metadata
from ..models import notification as notification_model  # register metadata
from ..models import review as review_model  # register metadata
from ..schemas import promotion as promotion_schema
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


def test_create_and_list_promotions(db_session):
    promo_req = promotion_schema.PromotionCreate(
        promo_code="SAVE10",
        discount_percent=10,
    )
    created = promotions_controller.create(db_session, promo_req)
    assert created.id is not None
    assert created.promo_code == "SAVE10"

    all_promos = promotions_controller.read_all(db_session)
    assert len(all_promos) == 1
    assert all_promos[0].promo_code == "SAVE10"


def test_apply_promo_to_user_order(db_session):
    # Seed user and menu item
    user = user_model.User(
        name="Promo User",
        email="promo@example.com",
        phone="111",
        address="Addr",
        password="hashed",
        role="customer",
    )
    item = menu_model.MenuItem(name="Pizza", description="Cheese", price=20.0)
    db_session.add_all([user, item])
    db_session.commit()

    promotions_controller.create(
        db_session,
        promotion_schema.PromotionCreate(promo_code="HALF", discount_percent=50),
    )

    order = orders_controller.create(
        db_session,
        order_schema.OrderCreate(
            user_id=user.id,
            items=[order_schema.OrderItem(menu_item_id=item.id, quantity=1)],
            promo_code="HALF",
        ),
    )

    assert order.total_price == pytest.approx(10.0)
    assert order.promotion_code == "HALF"
    assert order.promotion_discount == pytest.approx(50)


def test_apply_promo_to_guest_order(db_session):
    item = menu_model.MenuItem(name="Sandwich", description="Tasty", price=12.0)
    db_session.add(item)
    db_session.commit()

    promotions_controller.create(
        db_session,
        promotion_schema.PromotionCreate(promo_code="TENOFF", discount_percent=10),
    )

    order = orders_controller.create_guest_order(
        db_session,
        order_schema.GuestOrderCreate(
            guest_name="Guest Promo",
            items=[order_schema.OrderItem(menu_item_id=item.id, quantity=2)],
            promo_code="TENOFF",
        ),
    )

    assert order.total_price == pytest.approx(21.6)  # 24 * 0.9
    assert order.promotion_code == "TENOFF"
