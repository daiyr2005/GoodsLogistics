from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from mysite.db.model import Category, Store
from mysite.db.schema import Message, StoreIn, StoreOut
from .deps import get_db, get_or_404

router = APIRouter(prefix="/store", tags=["store"])


@router.get("/", response_model=list[StoreOut])
def get_all(category_id: int | None = None, db: Session = Depends(get_db)):
    query = select(Store)
    if category_id is not None:
        query = query.where(Store.category_id == category_id)
    return db.scalars(query).all()


@router.get("/{store_id}", response_model=StoreOut)
def get_one(store_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Store, store_id)


@router.post("/", response_model=Message[StoreOut], status_code=201)
def create(data: StoreIn, db: Session = Depends(get_db)):
    get_or_404(db, Category, data.category_id)
    obj = Store(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"message": "Магазин добавлен", "data": obj}


@router.put("/{store_id}", response_model=Message[StoreOut])
def update(store_id: int, data: StoreIn, db: Session = Depends(get_db)):
    obj = get_or_404(db, Store, store_id)
    get_or_404(db, Category, data.category_id)
    for field, value in data.model_dump().items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return {"message": "Магазин изменён", "data": obj}


@router.delete("/{store_id}", response_model=Message)
def delete(store_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, Store, store_id))
    db.commit()
    return {"message": "Магазин удалён"}