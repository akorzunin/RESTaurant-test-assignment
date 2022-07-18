from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel, EmailStr
import os

from db import crud, shemas
from db.db_connector import db

from dotenv import load_dotenv
load_dotenv()

class EmailSchema(BaseModel):
    email: list[EmailStr]


conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD'),
    MAIL_FROM = os.getenv('MAIL_FROM'),
    MAIL_SERVER = os.getenv('MAIL_SERVER'),
    MAIL_PORT = int(os.getenv('MAIL_PORT')),
    MAIL_TLS = True,
    MAIL_SSL = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

async def send_email_by_username(username: str, subject: str, mail_text: str):
    get_user = await db["users"].find_one(dict(username=username))
    message = MessageSchema(
        subject=subject,
        recipients=[get_user['email']],  # List of recipients, as many as you can pass 
        html=mail_text,
    )
    fm = FastMail(conf)
    await fm.send_message(message)

async def send_email_to_admins(subject: str, mail_text: str):
    admins = await db["users"].find(dict(is_admin=True)).to_list(1000)
    admin_mails = [admin['email'] for admin in admins]
    message = MessageSchema(
        subject=subject,
        recipients=admin_mails,  # List of recipients, as many as you can pass 
        html=mail_text,
    )
    fm = FastMail(conf)
    await fm.send_message(message)