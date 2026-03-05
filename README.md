# Dayflow Backend API

This is the FastAPI backend for the Dayflow application, using MongoDB for the database.

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
│   │   └── student.py   (Pydantic schemas and validation)
│   ├── routers/         (Controllers)
│   │   └── student.py   (HTTP endpoints, request/response handling)
│   └── services/        (Business Logic)
│       └── student.py   (Database operations, complex logic)
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

3. Ensure you have your `.env` file configured in the root `dayflow-backend/` directory with your MongoDB connection string:
   ```env
   MONGO_URI=mongodb://localhost:27017  # Or your actual connection string
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
