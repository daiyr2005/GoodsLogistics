from sqladmin import ModelView

from mysite.db.model import (
    Category,
    City,
    Deliver,
    Order,
    Product,
    RefreshToken,
    Review,
    Store,
    User,
    Warehouse,
)


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.email, User.status, User.created_date]


class RefreshTokenAdmin(ModelView, model=RefreshToken):
    column_list = [RefreshToken.id, RefreshToken.user_id, RefreshToken.created_date]


class CategoryAdmin(ModelView, model=Category):
    column_list = [Category.id, Category.category_name]


class StoreAdmin(ModelView, model=Store):
    column_list = [Store.id, Store.store_name, Store.category_id]


class ProductAdmin(ModelView, model=Product):
    column_list = [Product.id, Product.product_name, Product.store_id, Product.price, Product.is_original]


class ReviewAdmin(ModelView, model=Review):
    column_list = [Review.id, Review.store_id, Review.user_id, Review.stars]


class CityAdmin(ModelView, model=City):
    column_list = [City.id, City.city_name]


class OrderAdmin(ModelView, model=Order):
    column_list = [Order.id, Order.product_id, Order.user_id, Order.city_id, Order.quantity, Order.total_price]


class WarehouseAdmin(ModelView, model=Warehouse):
    column_list = [Warehouse.id, Warehouse.sklad_code, Warehouse.city_id, Warehouse.street]


class DeliverAdmin(ModelView, model=Deliver):
    column_list = [Deliver.id, Deliver.user_id, Deliver.warehouse_id]