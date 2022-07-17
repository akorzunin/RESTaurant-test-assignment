

from fastapi import APIRouter, Depends, FastAPI, Body, HTTPException, Response, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from routes.admin import get_current_active_user

from db import crud, shemas
from db.db_connector import db, client
from utils.password import hash_password



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
    created, new_user = await crud.create_user(db, user)
    if created:
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=new_user)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, 
        content=dict(message=f'user {new_user["username"]} already exist')
    )

@router.put(
    path="/{id}", 
    response_description="Update a user", 
    response_model=shemas.UserModel,
)
async def update_user(id: str, user: shemas.UpdateUserModel = Body(...)):
    if new_user := await crud.update_user(db, id, user):
        return new_user
    raise HTTPException(status_code=404, detail=f"user {id} not found")

@router.delete("/{id}", response_description="Delete a user")
async def delete_user(id: str):
    if await crud.delete_user_by_id(db, id):
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail=f"user {id} not found")

### 
@router.get("/check", response_description="Check db", )
async def check():
    return await client.server_info()


