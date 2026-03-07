from fastapi import APIRouter, Body, HTTPException, status
from datetime import datetime
from pydantic import BaseModel
from app.models.user import UserModel
from app.core.database import db
from app.core.firebase import verify_firebase_token
from app.services.user_service import generate_username

router = APIRouter(prefix="/auth", tags=["auth"])
user_collection = db.get_collection("users")

class SyncRequest(BaseModel):
    idToken: str

@router.post("/sync", response_model=UserModel)
async def sync_user(request: SyncRequest = Body(...)):
    """
    Synchronizes a Firebase user with the MongoDB database.
    Always generates a new username and stores it in our DB.
    """
    decoded_token = verify_firebase_token(request.idToken)
    uid = decoded_token.get("uid")
    email = decoded_token.get("email")
    name = decoded_token.get("name", "User")

    if not uid or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token missing uid or email"
        )

    # Check if user already exists
    existing_user = await user_collection.find_one({"uid": uid})

    if existing_user:        
        updates = {}
        if "username" not in existing_user:
            new_username = generate_username(name)
            updates["username"] = new_username
            existing_user["username"] = new_username
            
        if "createdAt" not in existing_user:
            created_at = datetime.utcnow().isoformat()
            updates["createdAt"] = created_at
            existing_user["createdAt"] = created_at
            
        if updates:
            await user_collection.update_one(
                {"uid": uid},
                {"$set": updates}
            )
        
        return existing_user

    # Create new user
    new_username = generate_username(name)
    new_user = UserModel(
        uid=uid,
        username=new_username,
        name=name,
        email=email
    )
    
    user_dict = new_user.model_dump(by_alias=True, exclude=["id"])
    await user_collection.insert_one(user_dict)
    return user_dict

@router.delete("/{uid}", response_description="Delete user and all associated data")
async def delete_user_data(uid: str):
    """
    Deletes the user from the users collection and all their rituals from the rituals collection.
    """
    # Delete the user document
    user_result = await user_collection.delete_one({"uid": uid})
    
    # Delete the user's rituals document
    ritual_collection = db.get_collection("rituals")
    ritual_result = await ritual_collection.delete_one({"uid": uid})
    
    if user_result.deleted_count == 0 and ritual_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"No data found for user {uid}")
        
    return {"message": f"Successfully deleted data for user {uid}"}
