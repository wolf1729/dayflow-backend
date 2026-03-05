from fastapi import FastAPI
from app.routers import student

app = FastAPI(
    title="Dayflow API",
    summary="A sample application showing how to use FastAPI to add a ReST API to a MongoDB collection.",
)

# Include the routers
app.include_router(student.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Dayflow API"}
