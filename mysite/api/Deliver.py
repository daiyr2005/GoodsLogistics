from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from mysite.db.model import Deliver, User, Warehouse
from mysite.db.schema import DeliverIn, DeliverOut, Message
from .deps import get_db, get_or_404

router = APIRouter(prefix="/deliver", tags=["deliver"])


@router.get("/", response_model=list[DeliverOut])
def get_all(user_id: int | None = None, warehouse_id: int | None = None,
            db: Session = Depends(get_db)):
    query = select(Deliver)
    if user_id is not None:
        query = query.where(Deliver.user_id == user_id)
    if warehouse_id is not None:
        query = query.where(Deliver.warehouse_id == warehouse_id)
    return db.scalars(query).all()


@router.get("/{deliver_id}", response_model=DeliverOut)
def get_one(deliver_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Deliver, deliver_id)


@router.post("/", response_model=Message[DeliverOut], status_code=201)
def create(data: DeliverIn, db: Session = Depends(get_db)):
    get_or_404(db, User, data.user_id)
    get_or_404(db, Warehouse, data.warehouse_id)
    obj = Deliver(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"message": "Доставка добавлена", "data": obj}


@router.delete("/{deliver_id}", response_model=Message)
def delete(deliver_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, Deliver, deliver_id))
    db.commit()
    return {"message": "Доставка удалена"}