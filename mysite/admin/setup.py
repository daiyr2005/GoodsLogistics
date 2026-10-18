from fastapi import FastAPI
from sqladmin import Admin

from mysite.db.db import engine

from .views import (
    CategoryAdmin,
    CityAdmin,
    DeliverAdmin,
    OrderAdmin,
    ProductAdmin,
    RefreshTokenAdmin,
    ReviewAdmin,
    StoreAdmin,
    UserAdmin,
    WarehouseAdmin,
)


def setup_admin(user_app: FastAPI):
    admin = Admin(user_app, engine)
    admin.add_view(UserAdmin)
    admin.add_view(RefreshTokenAdmin)
    admin.add_view(CategoryAdmin)
    admin.add_view(StoreAdmin)
    admin.add_view(ProductAdmin)
    admin.add_view(ReviewAdmin)
    admin.add_view(CityAdmin)
    admin.add_view(OrderAdmin)
    admin.add_view(WarehouseAdmin)
    admin.add_view(DeliverAdmin)