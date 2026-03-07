from typing import Optional, List
from pydantic import ConfigDict, BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated
from bson import ObjectId
from datetime import datetime
import uuid

# Represents an ObjectId field in the database.
# Converts MongoDB's ObjectId to a plain string automatically.
PyObjectId = Annotated[str, BeforeValidator(str)]


class RitualItem(BaseModel):
    """
    Represents a single ritual entry inside a ritual list.

    Attributes:
        group       : The group/category this ritual belongs to (e.g. "health", "mindfulness").
        name        : The display name of the ritual (e.g. "Morning Run").
        completedOn : A list of dates recording when this ritual was completed.
        createdAt   : The date when the ritual was created.
        isCounter   : Whether this ritual tracks a count instead of simply marking completed.
        unit        : The unit of the counter, like 'liters', 'glasses', 'pushups'.
        countLogs   : Map from YYYY-MM-DD date string to a numerical count. E.g. {'2024-01-01': 5.0}
    """

    ritual_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for the ritual")
    group: str = Field(..., description="The group or category this ritual belongs to")
    name: str = Field(..., description="The name of the ritual")
    completedOn: List[str] = Field(default=[], description="List of dates when the ritual was completed")
    createdAt: str = Field(..., description="The date when the ritual was created")
    isCounter: bool = Field(default=False, description="Whether this ritual tracks a count instead of simply marking completed")
    unit: Optional[str] = Field(default=None, description="The unit of the counter, like 'liters', 'glasses', 'pushups'")
    countLogs: dict[str, float] = Field(default={}, description="Map from YYYY-MM-DD date string to a numerical count. E.g. {'2024-01-01': 5.0}")


class RitualModel(BaseModel):
    """
    Container for a single user's ritual record stored in MongoDB.

    Each user has one RitualModel document identified by their uid.
    Rituals are split into 3 lists based on their current state:
        - activeRitual   : Rituals the user is currently practicing.
        - deletedRitual  : Rituals the user has deleted.
        - archivedRitual : Rituals the user has archived for later.

    Attributes:
        id             : MongoDB document ObjectId, aliased from '_id'. Auto-assigned by MongoDB.
        uid            : Unique user identifier linking this record to a user account.
        activeRitual   : List of active RitualItem objects.
        deletedRitual  : List of deleted RitualItem objects.
        archivedRitual : List of archived RitualItem objects.
    """

    id: Optional[PyObjectId] = Field(alias="_id", default=None, description="MongoDB document ID")
    uid: str = Field(..., description="Unique user ID this ritual record belongs to")
    activeRitual: List[RitualItem] = Field(..., description="List of currently active rituals")
    dailyStreak: List[str] = Field(default=[], description="List of dates when all daily rituals were completed")
    deletedRitual: List[RitualItem] = Field(..., description="List of deleted rituals")
    archivedRitual: List[RitualItem] = Field(..., description="List of archived rituals")

    model_config = ConfigDict(
        populate_by_name=True,        # allows using both 'id' and '_id' to set the id field
        arbitrary_types_allowed=True, # allows non-standard types like ObjectId
        json_schema_extra={
            "example": {
                "uid": "1234567890",
                "activeRitual": [
                    {"group": "health", "name": "Morning Run", "completedOn": ["2024-01-01", "2024-01-02"], "createdAt": "2024-01-01"},
                    {"group": "mindfulness", "name": "Meditation", "completedOn": [], "createdAt": "2024-01-01"},
                    {"group": "health", "name": "Drink Water", "createdAt": "2024-01-01", "isCounter": True, "unit": "liters", "countLogs": {"2024-01-01": 2.5, "2024-01-02": 3.0}},
                ],
                "deletedRitual": [
                    {"group": "health", "name": "Cold Shower", "completedOn": [], "createdOn": "2024-01-01"},
                ],
                "archivedRitual": [
                    {"group": "productivity", "name": "Journaling", "completedOn": ["2024-01-02"], "createdOn": "2024-01-01"},
                ],
            }
        },
    )

class DeleteGroupRequest(BaseModel):
    uid: str
    group_name: str