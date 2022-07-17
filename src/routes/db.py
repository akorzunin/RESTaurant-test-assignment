

from fastapi import APIRouter, Depends, FastAPI, Body, HTTPException, Response, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from routes.admin import get_current_active_user

from routes import shemas
from routes.db_connector import db, client
from routes.admin import hash_password



router = APIRouter()
### USERS
@router.get(
    path="/all_users", 
    response_description="List all users", 
    response_model=list[shemas.UserModel],
)
async def list_users():
    return await db["users"].find().to_list(1000)

@router.post(
    path="/create_user", 
    response_description="Add new user res", 
    response_model=shemas.UserModel,
)
async def create_user(
    user: shemas.UserModel = Body(...), 
    current_user: shemas.UserModel = Depends(get_current_active_user),
):
    '''Add new user '''
    user = jsonable_encoder(user)
    user['hashed_password'] = hash_password(user['hashed_password'])
    new_user = await db["users"].insert_one(user)
    created_user = await db["users"].find_one({"_id": new_user.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_user)

### 
@router.get("/check", response_description="Check db", )
async def check():
    return await client.server_info()


