
import asyncio
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from db.db_connector import db
from db import crud, shemas
from utils.password import hash_password
from utils import mail_handle

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


async def get_current_admin_user(current_user: shemas.UserModel = Depends(get_current_user)):
    if current_user.is_admin:
        return current_user 
    raise HTTPException(status_code=400, detail="Inactive user")

async def get_current_any_user(current_user: shemas.UserModel = Depends(get_current_user)):
    return current_user 

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
async def read_users_me(current_user: shemas.UserModel = Depends(get_current_admin_user)):
    return current_user

# set table reserved
@router.put(
    path="/reserve_table/{id}", 
    response_description="Reserve/unreserve a table", 
    response_model=shemas.TableModel,
)
async def reserve_table(
    table_id: str, 
    is_reserved: bool = True, 
    current_user: shemas.UserModel = Depends(get_current_user),
):
    '''Set table reserved'''
    if await db["tables"].find_one(dict(_id=table_id)):
        return await crud.update_table(
            db=db, 
            id=table_id, 
            table=shemas.UpdateTableModel(is_reserved=is_reserved)
        )
    raise HTTPException(status_code=404, detail=f"table {table_id} not found")

# avaliable/unavaliable table
@router.put(
    path="/block_table/{id}", 
    response_description="avaliable/unavaliable a table", 
    response_model=shemas.TableModel,
)
async def block_table(
    table_id: str, 
    is_avaliable: bool = False, 
    current_user: shemas.UserModel = Depends(get_current_user),
):
    '''Set table avaliable/unavaliable'''
    if await db["tables"].find_one(dict(_id=table_id)):
        return await crud.update_table(
            db=db, 
            id=table_id, 
            table=shemas.UpdateTableModel(is_avaliable=is_avaliable)
        )
    raise HTTPException(status_code=404, detail=f"table {table_id} not found")

# set table price
@router.put(
    path="/table_price/{id}", 
    response_description="set table price", 
    response_model=shemas.TableModel,
)
async def set_table_price(
    table_id: str, 
    price: float, 
    current_user: shemas.UserModel = Depends(get_current_user),
):
    '''Set table price'''
    if await db["tables"].find_one(dict(_id=table_id)):
        return await crud.update_table(
            db=db, 
            id=table_id, 
            table=shemas.UpdateTableModel(price=price)
        )
    raise HTTPException(status_code=404, detail=f"table {table_id} not found")

@router.patch(
    path="/confirm_reservation/", 
    response_description="confirm reservation for a table", 
    response_model=shemas.TableModel,
)
async def confirm_reservation(
    table_name: str, 
    username: str, 
    current_user: shemas.UserModel = Depends(get_current_user),
):
    '''Set table reserved'''
    if table := await db["tables"].find_one(dict(table_name=table_name)):
        await crud.update_table(
            db=db, 
            id=table['_id'], 
            table=shemas.UpdateTableModel(is_reserved=True)
        )
    else:
        raise HTTPException(status_code=404, detail=f"table {table_name} not found")
    if  user := await db["users"].find_one(dict(username=username)):
        # send mail to user that table is reserved
        user_mail = mail_handle.send_email_by_username(
                username=username,
                subject=f"Reserve {table['table_name']}", 
                mail_text=f"{table['table_name']} is successfully reserved",
            )
        asyncio.gather(user_mail)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, 
            content=f"{table['table_name']} is successfully reserved"
        )
    raise HTTPException(status_code=404, detail=f"User {username} not found")
