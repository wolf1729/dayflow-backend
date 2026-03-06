from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import Response
from bson import ObjectId
from typing import List
from datetime import date

from app.models.ritual import RitualItem, RitualModel
from app.core.database import db

router = APIRouter(prefix="/rituals", tags=["rituals"])
ritual_collection = db.get_collection("rituals")

@router.post(
    "/{uid}",
    response_description="Add a new ritual to a user's collection",
    response_model=RitualModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def add_ritual(uid: str, ritual_item: RitualItem = Body(...)):
    """
    Adds a new ritual to the 'activeRitual' list for the given user ID (uid).
    If no ritual record exists for the user, one is created.
    """
    # Check if the user's ritual record already exists
    existing_record = await ritual_collection.find_one({"uid": uid})
    
    # Prepare the ritual item data
    # Ensure dates are handled if they are not already (Pydantic usually handles this)
    ritual_data = ritual_item.model_dump()
    
    if existing_record:
        # Append to activeRitual list
        result = await ritual_collection.find_one_and_update(
            {"uid": uid},
            {"$push": {"activeRitual": ritual_data}},
            return_document=True
        )
        return result
    else:
        # Create a new record for the user
        new_record = RitualModel(
            uid=uid,
            activeRitual=[ritual_item],
            deletedRitual=[],
            archivedRitual=[]
        )
        new_record_dict = new_record.model_dump(by_alias=True, exclude=["id"])
        await ritual_collection.insert_one(new_record_dict)
        return new_record_dict

@router.get(
    "/{uid}",
    response_description="Get all rituals for a user",
    response_model=RitualModel,
    response_model_by_alias=False,
)
async def get_user_rituals(uid: str):
    """
    Retrieves the complete ritual record for the specified user ID (uid).
    """
    if (record := await ritual_collection.find_one({"uid": uid})) is not None:
        return record
    
    # If no record exists, return an empty RitualModel for that UID
    return RitualModel(
        uid=uid,
        activeRitual=[],
        deletedRitual=[],
        archivedRitual=[]
    )

@router.patch(
    "/{uid}/archive/{ritual_name}",
    response_description="Archive a ritual",
    response_model=RitualModel,
    response_model_by_alias=False,
)
async def archive_ritual(uid: str, ritual_name: str):
    """
    Moves a ritual from 'activeRitual' to 'archivedRitual'.
    """
    # Find the user record
    record = await ritual_collection.find_one({"uid": uid})
    if not record:
        raise HTTPException(status_code=404, detail=f"User {uid} not found")

    # Find the ritual in activeRitual
    active_rituals = record.get("activeRitual", [])
    ritual_to_archive = next((r for r in active_rituals if r["name"] == ritual_name), None)

    if not ritual_to_archive:
        raise HTTPException(status_code=404, detail=f"Ritual '{ritual_name}' not found in active rituals")

    # Move from active to archived
    result = await ritual_collection.find_one_and_update(
        {"uid": uid},
        {
            "$pull": {"activeRitual": {"name": ritual_name}},
            "$push": {"archivedRitual": ritual_to_archive}
        },
        return_document=True
    )
    return result

@router.patch(
    "/{uid}/delete/{ritual_name}",
    response_description="Delete a ritual (move to deleted)",
    response_model=RitualModel,
    response_model_by_alias=False,
)
async def delete_ritual(uid: str, ritual_name: str):
    """
    Moves a ritual from 'activeRitual' or 'archivedRitual' to 'deletedRitual'.
    """
    record = await ritual_collection.find_one({"uid": uid})
    if not record:
        raise HTTPException(status_code=404, detail=f"User {uid} not found")

    # Check activeRitual first, then archivedRitual
    ritual_to_delete = None
    source_list = None

    active_rituals = record.get("activeRitual", [])
    ritual_to_delete = next((r for r in active_rituals if r["name"] == ritual_name), None)
    if ritual_to_delete:
        source_list = "activeRitual"
    else:
        archived_rituals = record.get("archivedRitual", [])
        ritual_to_delete = next((r for r in archived_rituals if r["name"] == ritual_name), None)
        if ritual_to_delete:
            source_list = "archivedRitual"

    if not ritual_to_delete:
        raise HTTPException(status_code=404, detail=f"Ritual '{ritual_name}' not found in active or archived rituals")

    # Move from source list to deletedRitual
    result = await ritual_collection.find_one_and_update(
        {"uid": uid},
        {
            "$pull": {source_list: {"name": ritual_name}},
            "$push": {"deletedRitual": ritual_to_delete}
        },
        return_document=True
    )
    return result
