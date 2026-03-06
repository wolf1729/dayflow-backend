import os
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, status

import json

# Path to service account key file
# The user should place the serviceAccountKey.json in app/core/
SERVICE_ACCOUNT_PATH = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")

# Environment variable for Firebase Service Account JSON (as a string)
FIREBASE_SERVICE_ACCOUNT_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

if not firebase_admin._apps:
    if os.path.exists(SERVICE_ACCOUNT_PATH):
        try:
            cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            print(f"ERROR: Failed to initialize Firebase with file: {str(e)}")
    elif FIREBASE_SERVICE_ACCOUNT_JSON:
        try:
            # Parse the JSON string from the environment variable
            service_account_info = json.loads(FIREBASE_SERVICE_ACCOUNT_JSON)
            cred = credentials.Certificate(service_account_info)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            print(f"ERROR: Failed to initialize Firebase with environment variable: {str(e)}")
    else:
        # Fallback to default credentials (e.g. from environment variable GOOGLE_APPLICATION_CREDENTIALS)
        # Or initialize without credentials if running in a Google Cloud environment
        try:
            firebase_admin.initialize_app()
        except Exception:
            # We'll log a warning instead of crashing, as the user might be setting it up later
            print("WARNING: Firebase Admin SDK could not be initialized. Please provide serviceAccountKey.json or FIREBASE_SERVICE_ACCOUNT_JSON")

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
