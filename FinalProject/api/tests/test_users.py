import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..dependencies.database import Base
from ..controllers import users as users_controller
from ..models import user as user_model
from ..models import menu_item as menu_model  # register relationships
from ..models import order as order_model  # register relationships
from ..models import order_details as order_details_model  # register relationships
from ..models import payment as payment_model  # register relationships
from ..models import notification as notification_model  # register relationships
from ..models import promotion as promotion_model  # register relationships
from ..models import review as review_model  # register relationships


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


def test_read_users(db_session):
    user1 = user_model.User(
        name="Test User",
        email="user1@example.com",
        phone="123",
        address="Addr",
        password="hashed",
        role="customer",
    )
    user2 = user_model.User(
        name="Admin User",
        email="admin@example.com",
        phone="456",
        address="Addr2",
        password="hashed2",
        role="admin",
    )
    db_session.add_all([user1, user2])
    db_session.commit()

    all_users = users_controller.read_all(db_session)
    assert len(all_users) == 2
    assert {u.email for u in all_users} == {"user1@example.com", "admin@example.com"}

    fetched = users_controller.read_one(db_session, user1.id)
    assert fetched.name == "Test User"
