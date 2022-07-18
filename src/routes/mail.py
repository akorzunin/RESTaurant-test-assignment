from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Form
from starlette.responses import JSONResponse
from starlette.requests import Request

from utils import mail_handle

router = APIRouter()

@router.post("/email_to_user")
async def simple_send(
    username: str,
    subject: str,
    mail_text: str,
) -> JSONResponse:
    '''Send an email to user'''
    await mail_handle.send_email_by_username(username, subject, mail_text)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})

@router.post("/email_to_admins")
async def send_to_admins(
    subject: str,
    mail_text: str,
) -> JSONResponse:
    '''Send an email to user'''
    await mail_handle.send_email_to_admins(subject, mail_text)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})
