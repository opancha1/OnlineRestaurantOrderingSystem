import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..controllers import menu_items as controller
from ..schemas import menu_item as schema
from ..dependencies.database import Base

# Import related models to register relationships on metadata
from ..models import menu_item as menu_model
from ..models import order as order_model
from ..models import order_details as order_details_model
from ..models import user as user_model
from ..models import review as review_model
from ..models import payment as payment_model


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


def test_create_and_read_menu_item(db_session):
    request = schema.MenuItemCreate(
        name="BLT",
        description="Bacon lettuce tomato",
        price=7.5,
        category="sandwich",
        calories=550,
    )
    created = controller.create(db_session, request)
    assert created.id is not None
    assert created.name == "BLT"

    all_items = controller.read_all(db_session)
    assert len(all_items) == 1
    assert all_items[0].name == "BLT"


def test_update_menu_item(db_session):
    created = controller.create(
        db_session,
        schema.MenuItemCreate(name="Soup", description="Tomato", price=4.5, category="soup", calories=200),
    )
    updated = controller.update(
        db_session,
        created.id,
        schema.MenuItemCreate(name="Soup", description="Tomato", price=5.0, category="soup", calories=210),
    )
    assert updated.price == 5.0
    assert updated.calories == 210


def test_delete_menu_item(db_session):
    created = controller.create(
        db_session,
        schema.MenuItemCreate(name="Salad", description="Green", price=6.0, category="salad", calories=180),
    )
    controller.delete(db_session, created.id)
    remaining = controller.read_all(db_session)
    assert remaining == []
