from . import orders, order_details, menu_items, payments, notifications, promotions, analytics, users, reviews


def load_routes(app):
    app.include_router(orders.router)
    app.include_router(order_details.router)
    app.include_router(menu_items.router)
    app.include_router(payments.router)
    app.include_router(notifications.router)
    app.include_router(promotions.router)
    app.include_router(analytics.router)
    app.include_router(users.router)
    app.include_router(reviews.router)
