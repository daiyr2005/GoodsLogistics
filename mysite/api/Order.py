from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from mysite.db.model import City, Order, Product, User
from mysite.db.schema import Message, OrderIn, OrderOut
from .deps import get_db, get_or_404

router = APIRouter(prefix="/order", tags=["order"])


@router.get("/", response_model=list[OrderOut])
def get_all(user_id: int | None = None, skip: int = 0, limit: int = 50,
            db: Session = Depends(get_db)):
    query = select(Order)
    if user_id is not None:
        query = query.where(Order.user_id == user_id)
    return db.scalars(query.offset(skip).limit(limit)).all()


@router.get("/{order_id}", response_model=OrderOut)
def get_one(order_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Order, order_id)


@router.post("/", response_model=Message[OrderOut], status_code=201)
def create(data: OrderIn, db: Session = Depends(get_db)):
    product = get_or_404(db, Product, data.product_id)
    get_or_404(db, User, data.user_id)
    get_or_404(db, City, data.city_id)
    obj = Order(**data.model_dump(), total_price=product.price * data.quantity)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"message": "Заказ добавлен", "data": obj}


@router.put("/{order_id}", response_model=Message[OrderOut])
def update(order_id: int, data: OrderIn, db: Session = Depends(get_db)):
    obj = get_or_404(db, Order, order_id)
    product = get_or_404(db, Product, data.product_id)
    get_or_404(db, User, data.user_id)
    get_or_404(db, City, data.city_id)
    for field, value in data.model_dump().items():
        setattr(obj, field, value)
    obj.total_price = product.price * data.quantity
    db.commit()
    db.refresh(obj)
    return {"message": "Заказ изменён", "data": obj}


@router.delete("/{order_id}", response_model=Message)
def delete(order_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, Order, order_id))
    db.commit()
    return {"message": "Заказ удалён"}