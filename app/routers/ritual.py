from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import Response
from bson import ObjectId
from typing import List
from datetime import datetime
import traceback
import sys
from pydantic import BaseModel

from app.models.ritual import RitualItem, RitualModel, DeleteGroupRequest
from app.core.database import db

# Added this to the router file to keep request models close, or we can use generic dict, but BaseModel is better.
class CompleteRitualRequest(BaseModel):
    timestamp: str

router = APIRouter(prefix="/rituals", tags=["rituals"])
ritual_collection = db.get_collection("rituals")

@router.post(
    "/delete-group",
    response_description="Delete all active rituals in a specific group",
    response_model=RitualModel,
    response_model_by_alias=False,
)
async def delete_group_rituals(request: DeleteGroupRequest = Body(...)):
    """
    Moves all active rituals of a specific group to the deletedRitual list.
    """
    uid = request.uid
    group_name = request.group_name

    record = await ritual_collection.find_one({"uid": uid})
    if not record:
        raise HTTPException(status_code=404, detail=f"User {uid} not found")

    active_rituals = record.get("activeRitual", [])
    
    # Filter rituals: those to keep (active) and those to delete
    rituals_to_keep = []
    rituals_to_delete = []
    
    for r in active_rituals:
        if r.get("group") == group_name or (not r.get("group") and group_name == "General"):
            rituals_to_delete.append(r)
        else:
            rituals_to_keep.append(r)

    if not rituals_to_delete:
        # No rituals found to delete, just return the current record
        return record

    # Perform the update
    result = await ritual_collection.find_one_and_update(
        {"uid": uid},
        {
            "$set": {"activeRitual": rituals_to_keep},
            "$push": {"deletedRitual": {"$each": rituals_to_delete}}
        },
        return_document=True
    )
    return result


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
    try:
        # Check if the user's ritual record already exists
        existing_record = await ritual_collection.find_one({"uid": uid})
        
        # Prepare the ritual item data
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
    except Exception as e:
        print(f"Error in add_ritual for uid {uid}: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

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
    "/{uid}/archive/{ritual_id}",
    response_description="Archive a ritual",
    response_model=RitualModel,
    response_model_by_alias=False,
)
async def archive_ritual(uid: str, ritual_id: str):
    """
    Moves a ritual from 'activeRitual' to 'archivedRitual'.
    """
    # Find the user record
    record = await ritual_collection.find_one({"uid": uid})
    if not record:
        raise HTTPException(status_code=404, detail=f"User {uid} not found")

    # Find the ritual in activeRitual
    active_rituals = record.get("activeRitual", [])
    ritual_to_archive = next((r for r in active_rituals if r["ritual_id"] == ritual_id), None)

    if not ritual_to_archive:
        raise HTTPException(status_code=404, detail=f"Ritual ID '{ritual_id}' not found in active rituals")

    # Move from active to archived
    result = await ritual_collection.find_one_and_update(
        {"uid": uid},
        {
            "$pull": {"activeRitual": {"ritual_id": ritual_id}},
            "$push": {"archivedRitual": ritual_to_archive}
        },
        return_document=True
    )
    return result

@router.patch(
    "/{uid}/delete/{ritual_id}",
    response_description="Delete a ritual (move to deleted)",
    response_model=RitualModel,
    response_model_by_alias=False,
)
async def delete_ritual(uid: str, ritual_id: str):
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
    ritual_to_delete = next((r for r in active_rituals if r["ritual_id"] == ritual_id), None)
    if ritual_to_delete:
        source_list = "activeRitual"
    else:
        archived_rituals = record.get("archivedRitual", [])
        ritual_to_delete = next((r for r in archived_rituals if r["ritual_id"] == ritual_id), None)
        if ritual_to_delete:
            source_list = "archivedRitual"

    if not ritual_to_delete:
        raise HTTPException(status_code=404, detail=f"Ritual ID '{ritual_id}' not found in active or archived rituals")

    # Move from source list to deletedRitual
    result = await ritual_collection.find_one_and_update(
        {"uid": uid},
        {
            "$pull": {source_list: {"ritual_id": ritual_id}},
            "$push": {"deletedRitual": ritual_to_delete}
        },
        return_document=True
    )
    return result

@router.patch(
    "/{uid}/complete/{ritual_id}",
    response_description="Mark a ritual as complete for the day",
    response_model=RitualModel,
    response_model_by_alias=False,
)
async def complete_ritual(uid: str, ritual_id: str, request: CompleteRitualRequest = Body(...)):
    """
    Appends the given timestamp to the completedOn array of the specified active ritual.
    """
    record = await ritual_collection.find_one({"uid": uid})
    if not record:
        raise HTTPException(status_code=404, detail=f"User {uid} not found")

    active_rituals = record.get("activeRitual", [])
    target_ritual = next((r for r in active_rituals if r["ritual_id"] == ritual_id), None)
    
    if not target_ritual:
        raise HTTPException(status_code=404, detail=f"Ritual '{ritual_id}' not found in active rituals")

    # Update the specific ritual using array_filters
    result = await ritual_collection.find_one_and_update(
        {"uid": uid},
        {"$push": {"activeRitual.$[elem].completedOn": request.timestamp}},
        array_filters=[{"elem.ritual_id": ritual_id}],
        return_document=True
    )
    return result

class LogCountRequest(BaseModel):
    date: str
    count: float

@router.patch(
    "/{uid}/log-count/{ritual_id}",
    response_description="Log the current counter value for a specific date",
    response_model=RitualModel,
    response_model_by_alias=False,
)
async def log_ritual_count(uid: str, ritual_id: str, request: LogCountRequest = Body(...)):
    """
    Sets the count value for a specific date in the countLogs map of a counter ritual.
    """
    record = await ritual_collection.find_one({"uid": uid})
    if not record:
        raise HTTPException(status_code=404, detail=f"User {uid} not found")

    # The field path to update. Example: activeRitual.$[elem].countLogs.2024-03-07
    update_field = f"activeRitual.$[elem].countLogs.{request.date}"

    result = await ritual_collection.find_one_and_update(
        {"uid": uid},
        {"$set": {update_field: request.count}},
        array_filters=[{"elem.ritual_id": ritual_id}],
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Failed to update count for ritual {ritual_id}")
        
    return result

class UpdateStreakRequest(BaseModel):
    date: str

@router.patch(
    "/{uid}/update-streak",
    response_description="Add a date to the daily streak array",
    response_model=RitualModel,
    response_model_by_alias=False,
)
async def update_daily_streak(uid: str, request: UpdateStreakRequest = Body(...)):
    """
    Adds a specified date to the dailyStreak array if it is not already present.
    Called when a user completes all of their active rituals for the day.
    """
    record = await ritual_collection.find_one({"uid": uid})
    if not record:
        raise HTTPException(status_code=404, detail=f"User {uid} not found")

    result = await ritual_collection.find_one_and_update(
        {"uid": uid},
        {"$addToSet": {"dailyStreak": request.date}},
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=500, detail="Failed to update daily streak")
        
    return result

@router.get(
    "/{uid}/counter-insights",
    response_description="Get counter insights data for multi-line graphs",
)
async def get_counter_insights(uid: str):
    """
    Computes and returns data for a multi-line graph of counter rituals:
    - counterHabitsHistory: List of counter rituals and their history
    """
    record = await ritual_collection.find_one({"uid": uid})
    if not record:
        return {"counterHabitsHistory": []}

    active_rituals = record.get("activeRitual", [])
    archived_rituals = record.get("archivedRitual", [])
    all_rituals = active_rituals + archived_rituals

    counter_habits_history = []

    for r in all_rituals:
        if r.get("isCounter"):
            counter_habits_history.append({
                "ritual_id": r.get("ritual_id"),
                "name": r.get("name"),
                "unit": r.get("unit"),
                "history": r.get("countLogs", {})
            })

    return {
        "counterHabitsHistory": counter_habits_history
    }

@router.get(
    "/{uid}/insights",
    response_description="Get insights data for graphs",
)
async def get_insights(uid: str):
    """
    Computes and returns data for the Insights line graphs:
    - overallCompletionHistory: { "YYYY-MM-DD": total_completed }
    - dailyStreak: List of dates where all rituals were completed
    - counterHabitsHistory: List of counter rituals and their history
    """
    record = await ritual_collection.find_one({"uid": uid})
    if not record:
        # Return empty data structure if user has no rituals
        return {
            "overallCompletionHistory": {},
            "dailyStreak": [],
            "counterHabitsHistory": []
        }

    active_rituals = record.get("activeRitual", [])
    archived_rituals = record.get("archivedRitual", [])
    
    # We combine active and archived rituals to get a full history
    all_rituals = active_rituals + archived_rituals

    overall_completion_history = {}
    counter_habits_history = []

    for r in all_rituals:
        # 1. Aggregate overall completions
        completed_on = r.get("completedOn", [])
        for timestamp in completed_on:
            # Extract just the date part (YYYY-MM-DD)
            date_str = timestamp.split('T')[0]
            if date_str in overall_completion_history:
                overall_completion_history[date_str] += 1
            else:
                overall_completion_history[date_str] = 1

        # 2. Extract counter habitats
        if r.get("isCounter"):
            counter_habits_history.append({
                "ritual_id": r.get("ritual_id"),
                "name": r.get("name"),
                "unit": r.get("unit"),
                "history": r.get("countLogs", {})
            })

    return {
        "overallCompletionHistory": overall_completion_history,
        "dailyStreak": record.get("dailyStreak", []),
        "counterHabitsHistory": counter_habits_history
    }
