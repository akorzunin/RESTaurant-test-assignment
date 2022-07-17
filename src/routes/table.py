from fastapi import APIRouter, Depends, FastAPI, Body, HTTPException, Response, status
from fastapi.responses import JSONResponse

from routes.admin import get_current_active_user
from db import crud, shemas
from db.db_connector import db

router = APIRouter()
@router.get(
    path="/all_tables", 
    response_description="List all tables", 
    response_model=list[shemas.TableModel],
)
async def list_tables():
    return await db["tables"].find().to_list(1000)

@router.post(
    path="/create_table", 
    response_description="Add new table res", 
    response_model=shemas.TableModel,
)
async def create_table(
    table: shemas.TableModel = Body(...), 
    current_table: shemas.TableModel = Depends(get_current_active_user),
):
    '''Add new table '''
    created, new_table = await crud.create_table(db, table)
    if created:
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=new_table)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, 
        content=dict(message=f'table {new_table["table_name"]} already exist')
    )
@router.put(
    path="/{id}", 
    response_description="Update a table", 
    response_model=shemas.TableModel,
)
async def update_table(id: str, table: shemas.UpdateTableModel = Body(...)):
    if new_table := await crud.update_table(db, id, table):
        return new_table
    raise HTTPException(status_code=404, detail=f"table {id} not found")

@router.delete("/{id}", response_description="Delete a table")
async def delete_table(id: str):
    if await crud.delete_table_by_id(db, id):
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail=f"table {id} not found")
