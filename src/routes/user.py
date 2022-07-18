import asyncio
from typing import Literal
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse

from db.db_connector import db
from db import crud, shemas
from utils import mail_handle
from routes.admin import get_current_any_user

router = APIRouter()

# find table (table_type, num_of_seats, price, more/less)
@router.get(
    path="/find_table", 
    response_description="Find a table", 
    response_model=list[shemas.TableModel],
)
async def find_table(
    table_type: shemas.TableTypes,
    num_of_seats: int = 4,
    price: float = None,
    price_sort: Literal['higher_than', 'lower_than'] = 'lower_than',
):
    return await db["tables"]\
        .find(
            dict(
                table_type=table_type,
                is_reserved=False,
                is_avaliable=True,
                num_of_seats={'$gte': num_of_seats},
                price={
                    # change sort order 
                    '$lte' if price_sort == 'lower_than'
                    else '$gt' 
                    : price
                } if price 
                # find any if price not set
                else {'$gt':0},
            )    
        ).to_list(1000)
    
# reserve table
@router.post(
    path="/reserve_table", 
    response_description="Reserve a table", 
    response_model=shemas.UserModel,
)
async def reserve_table(
    table_id: str,
    current_user: shemas.UserModel = Depends(get_current_any_user),
):
    '''Reserve table for any user'''
    
    if await db['tables'].find_one(dict(
        _id=table_id,
        is_avaliable=True,
        is_reserved=False,
    )):
        table = await db['tables'].find_one(dict(_id=table_id))
        ### webhook placeholder
        # send mail to admin to accep/reject reservation
        mail_to_admin = mail_handle.send_email_to_admins(
            subject=f"Reserve Table request for user {current_user.username}",
            mail_text=f"User {current_user.username} asking for reservation for table {table['table_name']} <br> Go to /admin/confirm_reservation"
        )
        # send mail to user that we good
        mail_to_user = mail_handle.send_email_by_username(
            username=current_user.username,
            subject=f"Reserve {table['table_name']}", 
            mail_text=f"Reservation request for {table['table_name']} successfully sent",
        )
        asyncio.gather(mail_to_admin, mail_to_user)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, 
            content='Mail w/ confirmation link sent to admin'
        )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, 
        content=dict(message='Table not avaliable rn')
    )

# abort reservation
@router.post(
    path="/abort_reservation", 
    response_description="Aabort table reservation", 
    response_model=shemas.UserModel,
)
async def abort_reservation(
    table_id: str,
    current_user: shemas.UserModel = Depends(get_current_any_user),
):
    '''Aabort table reservation for any user'''
    
    if await db['tables'].find_one(dict(
        _id=table_id,
    )):
        table = await db['tables'].find_one(dict(_id=table_id))
        ### webhook placeholder
        # send mail to admin that user abort reservation
        mail_to_admin = mail_handle.send_email_to_admins(
            subject=f"User {current_user.username} aborted reservation for table {table['table_name']}",
            mail_text=f"User {current_user.username} is no longer asking for reservation for table {table['table_name']}",
        )
        # send mail to user that reservatioin aborted
        mail_to_user = mail_handle.send_email_by_username(
            username=current_user.username,
            subject=f"Abort reservation for {table['table_name']}", 
            mail_text=f"Reservation abort for {table['table_name']} is successfully accepted",
        )
        asyncio.gather(mail_to_admin, mail_to_user)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, 
            content='Reservation aborted'
        )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, 
        content=dict(message='No such table')
    )