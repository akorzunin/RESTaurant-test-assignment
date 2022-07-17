from pydantic import BaseModel, Field, EmailStr
from typing import Optional
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
        
class StudentModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    email: EmailStr = Field(...)
    course: str = Field(...)
    gpa: float = Field(..., le=4.0)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Jane Doe",
                "email": "jdoe@example.com",
                "course": "Experiments, Science, and Fashion in Nanophotonics",
                "gpa": "3.0",
            }
        }
        
class UpdateStudentModel(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    course: Optional[str]
    gpa: Optional[float]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Jane Doe",
                "email": "jdoe@example.com",
                "course": "Experiments, Science, and Fashion in Nanophotonics",
                "gpa": "3.0",
            }
        }

### users
user_example = {
    "username": "igor",
    "full_name": "Igor Novikov",
    "email": "igor@example.com",
    "hashed_password": "b'\\x0f\\xfe\\x1a\\xbd\\x1a\\x08!SS\\xc23\\xd6\\xe0\\ta>\\x95\\xee\\xc4%82\\xa7a\\xaf(\\xff7\\xacZ\\x15\\x0c'",
    "is_admin": False,
}

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
