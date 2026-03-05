from typing import Optional, List
from pydantic import ConfigDict, BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated
from bson import ObjectId

# Represents an ObjectId field in the database.
PyObjectId = Annotated[str, BeforeValidator(str)]

class UserModel(BaseModel):
    """
    Container for a single user record.
    """
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    uid: str = Field(...)
    name: str = Field(...)
    email: EmailStr = Field(...)
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "uid": "1234567890",
                "name": "Jane Doe",
                "email": "jdoe@example.com",
            }
        },
    )

class UpdateUserModel(BaseModel):
    """
    A set of optional updates to be made to a document in the database.
    """
    uid: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "uid": "1234567890",
                "name": "Jane Doe",
                "email": "jdoe@example.com",
            }
        },
    )

class UserCollection(BaseModel):
    """
    A container holding a list of `UserModel` instances.
    """
    users: List[UserModel]
