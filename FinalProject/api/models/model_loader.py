from ..dependencies.database import Base, engine
# Import model modules so SQLAlchemy registers them with the metadata
from . import (
    user,
    order,
    order_details,
    menu_item,
    payment,
    notification,
    review,
    promotion,
    recipes,
    sandwiches,
    resources,
)


def create_tables():
    Base.metadata.create_all(bind=engine)


def index():
    Base.metadata.create_all(engine)
