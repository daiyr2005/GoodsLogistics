from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from mysite.db.model import Category
from mysite.db.schema import CategoryIn, CategoryOut, Message
from .deps import get_db, get_or_404

router = APIRouter(prefix="/category", tags=["category"])


@router.get("/", response_model=list[CategoryOut])
def get_all(db: Session = Depends(get_db)):
    return db.scalars(select(Category)).all()


@router.get("/{category_id}", response_model=CategoryOut)
def get_one(category_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Category, category_id)


@router.post("/", response_model=Message[CategoryOut], status_code=201)
def create(data: CategoryIn, db: Session = Depends(get_db)):
    if db.scalar(select(Category).where(Category.category_name == data.category_name)):
        raise HTTPException(status_code=400, detail="Категория уже существует")
    obj = Category(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"message": "Категория добавлена", "data": obj}


@router.put("/{category_id}", response_model=Message[CategoryOut])
def update(category_id: int, data: CategoryIn, db: Session = Depends(get_db)):
    obj = get_or_404(db, Category, category_id)
    for field, value in data.model_dump().items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return {"message": "Категория изменена", "data": obj}


@router.delete("/{category_id}", response_model=Message)
def delete(category_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, Category, category_id))
    db.commit()
    return {"message": "Категория удалена"}