from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from mysite.db.model import Product, Store
from mysite.db.schema import Message, ProductIn, ProductOut
from .deps import get_db, get_or_404

router = APIRouter(prefix="/product", tags=["product"])


@router.get("/", response_model=list[ProductOut])
def get_all(store_id: int | None = None, skip: int = 0, limit: int = 50,
            db: Session = Depends(get_db)):
    query = select(Product)
    if store_id is not None:
        query = query.where(Product.store_id == store_id)
    return db.scalars(query.offset(skip).limit(limit)).all()


@router.get("/{product_id}", response_model=ProductOut)
def get_one(product_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Product, product_id)


@router.post("/", response_model=Message[ProductOut], status_code=201)
def create(data: ProductIn, db: Session = Depends(get_db)):
    get_or_404(db, Store, data.store_id)
    obj = Product(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"message": "Товар добавлен", "data": obj}


@router.put("/{product_id}", response_model=Message[ProductOut])
def update(product_id: int, data: ProductIn, db: Session = Depends(get_db)):
    obj = get_or_404(db, Product, product_id)
    get_or_404(db, Store, data.store_id)
    for field, value in data.model_dump().items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return {"message": "Товар изменён", "data": obj}


@router.delete("/{product_id}", response_model=Message)
def delete(product_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, Product, product_id))
    db.commit()
    return {"message": "Товар удалён"}