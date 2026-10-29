
import uvicorn
from fastapi import FastAPI

from mysite.admin.setup import setup_admin
from mysite.api import (
    Category,
    City,
    Deliver,
    Order,
    Product,
    Review,
    Store,
    Warehouse,
    auth,
    users,
    ai,
)
from mysite.db.db import Base, engine
from mysite.db.model import User

app = FastAPI(title="Auth Service")



app.include_router(auth.auth_router)
app.include_router(users.router)
app.include_router(Category.router)
app.include_router(City.router)
app.include_router(Store.router)
app.include_router(Product.router)
app.include_router(Review.router)
app.include_router(Order.router)
app.include_router(Warehouse.router)
app.include_router(Deliver.router)
app.include_router(ai.ai_router)

setup_admin(app)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8005)
