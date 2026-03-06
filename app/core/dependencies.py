from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.firebase import verify_firebase_token
from app.core.database import db

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency for protected routes.
    Verifies the Firebase ID token and retrieves the user from MongoDB.
    """
    token = credentials.credentials
    decoded_token = verify_firebase_token(token)
    
    uid = decoded_token.get("uid")
    if not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: uid mission"
        )
    
    user_collection = db.get_collection("users")
    user = await user_collection.find_one({"uid": uid})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in database. Please sync your account."
        )
    
    return user
