from pymongo import AsyncMongoClient
from app.core.config import settings

client = AsyncMongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]

def get_database():
    return db
