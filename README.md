# Dayflow Backend API

This is the FastAPI backend for the Dayflow application, using MongoDB for the database and Firebase for authentication.

**Deployed Server URL**: [https://dayflow-backend-llwn.onrender.com](https://dayflow-backend-llwn.onrender.com)

> [!NOTE]
> To keep the server alive, we are using **UptimeRobot** to ping the server every 10 minutes.

## Folder Structure

The application is structured for production-readiness, separating concerns into individual modules (Controller-Service-Model architecture):

```
dayflow-backend/
├── app/
│   ├── __init__.py      (Initializes the app module)
│   ├── main.py          (FastAPI app initialization and router inclusion)
│   ├── core/
│   │   ├── config.py    (Pydantic Settings for env vars like MONGO_URI)
│   │   └── database.py  (MongoDB client initialization)
│   ├── models/
│   │   ├── ritual.py    (Ritual Pydantic schemas)
│   │   └── user.py      (User Pydantic schemas)
│   ├── routers/         (Controllers)
│   │   ├── auth.py      (Authentication endpoints)
│   │   └── ritual.py    (Ritual management endpoints)
│   └── services/        (Business Logic)
│       └── ritual.py    (Database operations for rituals)
├── main.py              (Entry point script to run with uvicorn)
├── requirements.txt     (Project dependencies)
└── .env                 (Environment variables - ignored by git)
```

## Setup & Installation

1. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Ensure you have your `.env` file configured in the root `dayflow-backend/` directory:
   ```env
   MONGO_URI=your_mongodb_connection_string
   FIREBASE_SERVICE_ACCOUNT_JSON=path_to_service_account.json
   # Or provide firebase credentials as individual env vars if supported by your config
   ```

## Running the Server

You can start the development server using either of the following commands:

Using the modern FastAPI CLI (recommended):

```bash
fastapi dev app/main.py
```

Using the traditional Uvicorn wrapper script:

```bash
python main.py
```

## API Documentation

Once the server is running, FastAPI automatically generates interactive API documentation. You can access it at:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
