from fastapi import  APIRouter, HTTPException, Depends
from sqlalchemy.sql.functions import user
from sqlalchemy.util import deprecated
from  mysite.db.db import SessionLocal
from mysite.db.model import User, RefreshToken
from mysite.db.schema import UserCreate, UserOut, UserUpdate, UserLogin
from  sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from mysite.config import (SECRET_KEY, ALGORITHM, ACCESS_TOKEN_LIFETIME, REFRESH_TOKEN_LIFETIME)
from datetime import  timedelta, datetime
from  jose import jwt, JWTError
from  typing import Optional





pwd_contex = CryptContext(schemes=["bcrypt"], deprecated = "auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login")

auth_router = APIRouter(prefix='/auth', tags=['Auth'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

credentials_exception = HTTPException(
        status_code=401,
        detail="Access token туура эмес же мооноту бутту",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(token: str = Depends(oauth2_schema),db: Session = Depends(get_db),):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])

        subject = payload.get("sub")

        if subject is None:
            raise credentials_exception

        user_id = int(subject)

    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    user_db = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user_db is None:
        raise credentials_exception

    return user_db

def get_password_hash(password):#string
    return pwd_contex.hash(password)#befbejfejfejfghefhefhrehr

def verify_password(plain_password, hashed_password):
    return pwd_contex.verify(plain_password, hashed_password)

def create_access_token(date: dict, expires_delta: Optional[timedelta] = None):
    to_encode = date.copy()
    expires = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_LIFETIME))
    to_encode.update({'exp': expires})
    return  jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(date: dict):
    return create_access_token(date, expires_delta=timedelta(days=REFRESH_TOKEN_LIFETIME))




@auth_router.post('/register/', response_model=dict)
async  def register(user: UserCreate, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.username==user.username).first()
    email_db = db.query(User).filter(User.email==user.email).first()
    if  user_db or email_db:
        raise HTTPException(detail='Информация, которую вы написали, неверна.', status_code=401)

    hash_password = get_password_hash(user.password)
    print("Password:", user.password)
    print("Length:", len(user.password))
    user_data = User(
        username=user.username,
        email=user.email,
        password=hash_password

    )
    db.add(user_data)
    db.commit()
    db.refresh(user_data)
    return {'message': 'Вы зарегистрировались.'}

# @auth_router.post('/login/', response_model=dict)
# async def login(user: UserLogin, db: Session = Depends(get_db)):
#     user_db = db.query(User).filter(User.username == user.username).first()
#
#     if not user_db or not verify_password(user.password, user_db.password):
#         raise HTTPException(detail='Информация, которую вы написали, неверна.', status_code=404)
#
#
#     access_token = create_access_token({'sub': user_db.username})
#     refresh_token = create_access_token({'sub': user_db.username})
#
#     token_db = RefreshToken(user_id=user_db.id, token=refresh_token)
#     db.add(token_db)
#     db.commit()
#
#
#     return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'Bearer'}


@auth_router.post('/logout')
async def logout(refresh_token: str, db: Session = Depends(get_db)):

    stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()

    if not stored_token:
        raise HTTPException(status_code=420, detail='Maalymat tyyra emec')

    db.delete(stored_token)
    db.commit()

    return {"message": "Ийгиликту  чыкты"}



def get_token_data(user: User):
    return {'sub': str(user.id), 'username': user.username, 'status': user.status}

@auth_router.post('/login/', response_model=dict)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    user_db = (db.query(User).filter(User.username == user.username).first())
    if not user_db or not verify_password(user.password, user_db.password):
        raise HTTPException(detail='сиз жазган маалымат туура эмес', status_code=401)

    token_data = get_token_data(user_db)

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    token_db = RefreshToken(user_id=user_db.id, token=refresh_token)
    db.add(token_db)
    db.commit()



    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'Bearer'}






# @auth_router.post('/refresh')
# async def refresh(refresh_token: str, db:Session = Depends(get_db)):
#     stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
#     if not stored_token:
#         raise HTTPException(status_code=402, detail='Информация неверна')
#
#
#     access_token = create_access_token({'sub': stored_token.id})
#
#     return {'access_token': access_token, 'token_type': 'Bearer'}



@auth_router.post('/refresh/', response_model=dict)
async def refresh(refresh_token: str, db: Session = Depends(get_db),):
    stored_token = (db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first())

    if not stored_token:
        raise HTTPException(status_code=401, detail='Маалымат туура эмес')

    user_db = stored_token.token_user
    token_data = get_token_data(user_db)

    access_token = create_access_token(token_data)

    return {'access_token': access_token, 'token_type': 'Bearer'}

@auth_router.get('/verify/', response_model=UserOut)
async def verify_access_token(current_user: User = Depends(get_current_user)):
    return current_user



@auth_router.get('/me/', response_model=UserOut)
async def user_me(profile: User = Depends(get_current_user)):
    return profile

@auth_router.put("/me/update/")
def update_me(
    data:UserUpdate,
    db:Session=Depends(get_db),
    current_user=Depends(get_current_user)
):

    user=db.query(User).filter(
        User.id==current_user.id
    ).first()


    for key,value in data.dict().items():

        if value:
            setattr(
                user,
                key,
                value
            )


    db.commit()
    db.refresh(user)


    return user

@auth_router.delete("/me/")
def delete_me(
    db:Session=Depends(get_db),
    current_user=Depends(get_current_user)
):

    user=db.query(User).filter(
        User.id==current_user.id
    ).first()


    db.delete(user)
    db.commit()


    return {
        "message":"Аккаунт удалён"
    }