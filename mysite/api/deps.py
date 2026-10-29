from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from mysite.db.db    import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_or_404(db: Session, model, object_id: int):
    obj = db.get(model, object_id)

    if obj is None:
        raise HTTPException(status_code=404, detail="Not found")

    return obj