from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from mysite.db.model import City, Warehouse
from mysite.db.schema import Message, WarehouseIn, WarehouseOut
from .deps import get_db, get_or_404

router = APIRouter(prefix="/warehouse", tags=["warehouse"])


@router.get("/", response_model=list[WarehouseOut])
def get_all(city_id: int | None = None, db: Session = Depends(get_db)):
    query = select(Warehouse)
    if city_id is not None:
        query = query.where(Warehouse.city_id == city_id)
    return db.scalars(query).all()


@router.get("/{warehouse_id}", response_model=WarehouseOut)
def get_one(warehouse_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Warehouse, warehouse_id)


@router.post("/", response_model=Message[WarehouseOut], status_code=201)
def create(data: WarehouseIn, db: Session = Depends(get_db)):
    get_or_404(db, City, data.city_id)
    if db.scalar(select(Warehouse).where(Warehouse.sklad_code == data.sklad_code)):
        raise HTTPException(status_code=400, detail="Код склада уже существует")
    obj = Warehouse(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"message": "Склад добавлен", "data": obj}


@router.put("/{warehouse_id}", response_model=Message[WarehouseOut])
def update(warehouse_id: int, data: WarehouseIn, db: Session = Depends(get_db)):
    obj = get_or_404(db, Warehouse, warehouse_id)
    get_or_404(db, City, data.city_id)
    for field, value in data.model_dump().items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return {"message": "Склад изменён", "data": obj}


@router.delete("/{warehouse_id}", response_model=Message)
def delete(warehouse_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, Warehouse, warehouse_id))
    db.commit()
    return {"message": "Склад удалён"}