from fastapi import APIRouter, Depends, Form, HTTPException
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from mysite.db.db import SessionLocal  # поправьте под ваш проект
from mysite.db.model import User, UserStatus
from mysite.db.schema import UserOut, UserUpdate, MessageOut  # поправьте путь

router = APIRouter(prefix="/user", tags=["user"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_or_404(db: Session, user_id: int) -> User:
    obj = db.get(User, user_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return obj


@router.get("/", response_model=list[UserOut])
def get_all(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.scalars(select(User).offset(skip).limit(limit)).all()


@router.get("/{user_id}", response_model=UserOut)
def get_one(user_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, user_id)


@router.post("/", response_model=MessageOut, status_code=201)
def create(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(..., min_length=8),
    status: UserStatus = Form(UserStatus.buyer),
    db: Session = Depends(get_db),
):
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    if db.scalar(select(User).where(User.username == username)):
        raise HTTPException(status_code=400, detail="Username уже занят")

    obj = User(
        username=username,
        email=email,
        password=pwd_context.hash(password),
        status=status.value,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return MessageOut(message="Пользователь добавлен", data=obj)


@router.patch("/{user_id}", response_model=MessageOut)
def update(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, user_id)
    changes = data.model_dump(exclude_unset=True)

    if "email" in changes and changes["email"] != obj.email:
        if db.scalar(select(User).where(User.email == changes["email"])):
            raise HTTPException(status_code=400, detail="Email уже занят")

    if "username" in changes and changes["username"] != obj.username:
        if db.scalar(select(User).where(User.username == changes["username"])):
            raise HTTPException(status_code=400, detail="Username уже занят")

    if "password" in changes:
        changes["password"] = pwd_context.hash(changes["password"])
    if "status" in changes:
        changes["status"] = changes["status"].value

    for field, value in changes.items():
        setattr(obj, field, value)

    db.commit()
    db.refresh(obj)
    return MessageOut(message="Пользователь изменён", data=obj)


@router.delete("/{user_id}", response_model=MessageOut)
def delete(user_id: int, db: Session = Depends(get_db)):
    obj = get_or_404(db, user_id)
    db.delete(obj)
    db.commit()
    return MessageOut(message="Пользователь удалён")