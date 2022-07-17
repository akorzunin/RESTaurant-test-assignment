import hashlib

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from db.db_connector import db
from db import crud, shemas
from utils.password import hash_password
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/token")

async def get_user(db, username: str):
    user = await db["users"].find_one(dict(username=username))
    if user:
        return shemas.UserModel(**user)


def decode_token(token):
    return get_user(db, token)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = await decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: shemas.UserModel = Depends(get_current_user)):
    if current_user.is_admin:
        return current_user 
    raise HTTPException(status_code=400, detail="Inactive user")


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = await crud.get_user_by_username(db, form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = shemas.UserModel(**user_dict)
    hashed_password = hash_password(form_data.password)
    if hashed_password != user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@router.get("/users/me")
async def read_users_me(current_user: shemas.UserModel = Depends(get_current_active_user)):
    return current_user