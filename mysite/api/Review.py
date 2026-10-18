from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from mysite.db.model import Review, Store, User
from mysite.db.schema import Message, ReviewIn, ReviewOut
from .deps import get_db, get_or_404

router = APIRouter(prefix="/review", tags=["review"])


@router.get("/", response_model=list[ReviewOut])
def get_all(store_id: int | None = None, skip: int = 0, limit: int = 50,
            db: Session = Depends(get_db)):
    query = select(Review)
    if store_id is not None:
        query = query.where(Review.store_id == store_id)
    return db.scalars(query.offset(skip).limit(limit)).all()


@router.get("/{review_id}", response_model=ReviewOut)
def get_one(review_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Review, review_id)


@router.post("/", response_model=Message[ReviewOut], status_code=201)
def create(data: ReviewIn, db: Session = Depends(get_db)):
    get_or_404(db, Store, data.store_id)
    get_or_404(db, User, data.user_id)
    obj = Review(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"message": "Отзыв добавлен", "data": obj}


@router.put("/{review_id}", response_model=Message[ReviewOut])
def update(review_id: int, data: ReviewIn, db: Session = Depends(get_db)):
    obj = get_or_404(db, Review, review_id)
    for field, value in data.model_dump().items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return {"message": "Отзыв изменён", "data": obj}


@router.delete("/{review_id}", response_model=Message)
def delete(review_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, Review, review_id))
    db.commit()
    return {"message": "Отзыв удалён"}