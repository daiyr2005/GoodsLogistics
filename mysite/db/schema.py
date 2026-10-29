from datetime import datetime
from decimal import Decimal
from typing import Generic, TypeVar
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from mysite.db.model import UserStatus


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(..., min_length=8)
    status: str
    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8)
    status: UserStatus | None = None


class UserOut(ORMModel):
    id: int
    username: str
    email: EmailStr
    status: UserStatus
    created_date: datetime


T = TypeVar("T")


class Message(BaseModel, Generic[T]):
    message: str
    data: T | None = None


MessageOut = Message[UserOut]


class CategoryIn(BaseModel):
    category_name: str


class CategoryOut(ORMModel, CategoryIn):
    id: int


class StoreIn(BaseModel):
    store_name: str
    category_id: int
    store_image: str | None = None


class StoreOut(ORMModel, StoreIn):
    id: int


class ProductIn(BaseModel):
    store_id: int
    product_name: str
    price: Decimal = Field(..., gt=0)
    description: str | None = None
    is_original: bool = True


class ProductOut(ORMModel):
    id: int
    store_id: int
    product_name: str
    price: Decimal = Field(..., gt=0)
    description: str | None = None
    is_original: bool = True
    create_date: datetime


class ReviewIn(BaseModel):
    store_id: int
    user_id: int
    text: str
    stars: int = Field(..., ge=1, le=5)


class ReviewOut(ORMModel, ReviewIn):
    id: int
    created_date: datetime


class CityIn(BaseModel):
    city_name: str


class CityOut(ORMModel, CityIn):
    id: int


class OrderIn(BaseModel):
    product_id: int
    user_id: int
    city_id: int
    quantity: int = Field(1, ge=1)


class OrderOut(ORMModel, OrderIn):
    id: int
    total_price: Decimal
    created_date: datetime


class WarehouseIn(BaseModel):
    city_id: int
    sklad_code: str
    street: str


class WarehouseOut(ORMModel, WarehouseIn):
    id: int


class DeliverIn(BaseModel):
    user_id: int
    warehouse_id: int


class DeliverOut(ORMModel, DeliverIn):
    id: int


class ChatInputSchema(BaseModel):
    question: str = Field(..., min_length=1)


class ChatItemSchema(BaseModel):
    id: int
    product_name: str
    price: float
    store_id: int
    is_original: bool
    description: str | None = None


class ChatOutputSchema(BaseModel):
    answer: str
    items: list[ChatItemSchema] = Field(default_factory=list)