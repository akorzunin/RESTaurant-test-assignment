from pydantic import BaseModel, Field, EmailStr
from typing import Literal, Optional
from pymongo import MongoClient
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")
        

### USERS
user_example = dict(
    username="igor",
    full_name="Igor Novikov",
    email="igor@example.com",
    hashed_password="b'\\x0f\\xfe\\x1a\\xbd\\x1a\\x08!SS\\xc23\\xd6\\xe0\\ta>\\x95\\xee\\xc4%82\\xa7a\\xaf(\\xff7\\xacZ\\x15\\x0c'",
    is_admin=False,
)

class UserModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str = Field(...)
    full_name: str = Field(...)
    email: EmailStr = Field(...)
    hashed_password: str = Field(...)
    is_admin: bool = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": user_example,
        }

class UpdateUserModel(BaseModel):
    username: Optional[str]
    full_name: Optional[str]
    email: Optional[EmailStr]
    hashed_password: Optional[str]
    is_admin: Optional[bool]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": user_example,
        }
### TABLES
TableTypes = Literal['standard', 'cab', 'room']

table_example = dict(
    table_name='Table 1',
    table_type='standard',
    num_of_seats=4,
    is_avaliable=True,
    is_reserved=False,
    price=1000,
)
class TableModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    table_name: str = Field(...)
    table_type: TableTypes = Field(...) # standard cab room
    num_of_seats: int = Field(...)
    is_avaliable: bool = Field(...)
    is_reserved: bool = Field(...)
    price: float = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": table_example,
        }

class UpdateTableModel(BaseModel):
    table_name: Optional[str]
    table_type: Optional[TableTypes]
    num_of_seats: Optional[int]
    is_avaliable: Optional[bool]
    is_reserved: Optional[bool]
    price: Optional[float]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": table_example,
        }