from datetime import datetime
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
    username: str = Field(...)
    name: str = Field(...)
    email: EmailStr = Field(...)
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "uid": "1234567890",
                "name": "Jane Doe",
                "email": "jdoe@example.com",
                "createdAt": "2024-03-07T14:30:00.000Z"
            }
        },
    )