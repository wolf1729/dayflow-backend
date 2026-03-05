from pymongo import AsyncMongoClient
from app.core.config import settings

client = AsyncMongoClient(settings.MONGO_URI)
db = client.dayflow

def get_database():
    return db
