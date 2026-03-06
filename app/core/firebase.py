import os
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, status
from app.core.firebaseConfig import firebase_env_vars

if not firebase_admin._apps:
    initialized = False
    
    # 1. Try initializing with individual environment variables from firebaseConfig
    if firebase_env_vars.get("private_key") and firebase_env_vars.get("client_email"):
        try:
            # Filter out None values
            cred_dict = {k: v for k, v in firebase_env_vars.items() if v is not None}
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("INFO: Firebase initialized using FIREBASE_* env vars from firebaseConfig.py")
            initialized = True
        except Exception as e:
            print(f"ERROR: Failed to initialize Firebase with individual env vars: {str(e)}")

    # 2. Final fallback to default/project ID
    if not initialized:
        try:
            options = {}
            project_id = os.getenv("FIREBASE_PROJECT_ID")
            if project_id:
                options['projectId'] = project_id
            firebase_admin.initialize_app(options=options)
            print(f"INFO: Firebase initialized using default credentials. Project ID: {project_id or 'Not Set'}")
        except Exception as e:
            print(f"WARNING: Firebase Admin SDK could not be initialized: {str(e)}")
            print("Please ensure FIREBASE_* environment variables are set correctly.")

def verify_firebase_token(id_token: str):
    """
    Verifies the Firebase ID token and returns the decoded token.
    """
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Firebase token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
