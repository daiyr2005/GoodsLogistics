from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from mysite.db.model import City
from mysite.db.schema import CityIn, CityOut, Message
from .deps import get_db, get_or_404

router = APIRouter(prefix="/city", tags=["city"])


@router.get("/", response_model=list[CityOut])
def get_all(db: Session = Depends(get_db)):
    return db.scalars(select(City)).all()


@router.get("/{city_id}", response_model=CityOut)
def get_one(city_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, City, city_id)


@router.post("/", response_model=Message[CityOut], status_code=201)
def create(data: CityIn, db: Session = Depends(get_db)):
    if db.scalar(select(City).where(City.city_name == data.city_name)):
        raise HTTPException(status_code=400, detail="Город уже существует")
    obj = City(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"message": "Город добавлен", "data": obj}


@router.put("/{city_id}", response_model=Message[CityOut])
def update(city_id: int, data: CityIn, db: Session = Depends(get_db)):
    obj = get_or_404(db, City, city_id)
    for field, value in data.model_dump().items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return {"message": "Город изменён", "data": obj}


@router.delete("/{city_id}", response_model=Message)
def delete(city_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, City, city_id))
    db.commit()
    return {"message": "Город удалён"}