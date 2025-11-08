from . import orders, order_details, recipes, sandwiches, resources
from ..dependencies.database import Base, engine
from . import user, order, order_detail, menu_item, resource, payment, review, promotion

from ..dependencies.database import engine


def create_tables():
    Base.metadata.create_all(bind=engine)


def index():
    orders.Base.metadata.create_all(engine)
    order_details.Base.metadata.create_all(engine)
    recipes.Base.metadata.create_all(engine)
    sandwiches.Base.metadata.create_all(engine)
    resources.Base.metadata.create_all(engine)
