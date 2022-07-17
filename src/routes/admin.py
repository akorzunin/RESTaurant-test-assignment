import hashlib
from typing import Union

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from routes.db_connector import db
from routes import crud
from routes import shemas
router = APIRouter()

# fake_users_db = {
    # "johndoe": {
    #     "username": "johndoe",
    #     "full_name": "John Doe",
    #     "email": "johndoe@example.com",
    #     "hashed_password": 'b"+\\xb8\\rS{\\x1d\\xa3\\xe3\\x8b\\xd3\\x03a\\xaa\\x85V\\x86\\xbd\\xe0\\xea\\xcdqb\\xfe\\xf6\\xa2_\\xe9{\\xf5\'\\xa2["',
    #     "disabled": False,
    # },
#     "akorz": {
#         "username": "akorz",
#         "full_name": "Alexey Korzunin",
#         "email": "akorzunin123@gmail.com",
#         "hashed_password": 'b\'\\x9am\\x14\\x00\\xc18\\x1f\\xfe;;\\xa6\\xdb\\xb5\\xfa\\xc5\\xd7\\xf2\\xa1\\xe9\\x0b\\x14a!"^i\\xf7\\tW\\xaf\\xbc\\t\'',
#         "disabled": False,
#     },
#     "admin": {
#         "username": "admin",
#         "full_name": "admin",
#         "email": "aminmail@gmail.com",
#         "hashed_password": "b'\\x8civ\\xe5\\xb5A\\x04\\x15\\xbd\\xe9\\x08\\xbdM\\xee\\x15\\xdf\\xb1g\\xa9\\xc8s\\xfcK\\xb8\\xa8\\x1fo*\\xb4H\\xa9\\x18'",
#         "disabled": False,
#     },
#     "alice": {
#         "username": "alice",
#         "full_name": "Alice Wonderson",
#         "email": "alice@example.com",
#         "hashed_password": 'b"+\\xb8\\rS{\\x1d\\xa3\\xe3\\x8b\\xd3\\x03a\\xaa\\x85V\\x86\\xbd\\xe0\\xea\\xcdqb\\xfe\\xf6\\xa2_\\xe9{\\xf5\'\\xa2["',
#         "disabled": True,
#     },
# }

def hash_password(password: str) -> str:
    return str(hashlib.sha256(f"{password}".encode()).digest())

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/token")


# class User(BaseModel):
#     username: str
#     email: Union[str, None] = None
#     full_name: Union[str, None] = None
#     disabled: Union[bool, None] = None


# class UserInDB(User):
#     hashed_password: str


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