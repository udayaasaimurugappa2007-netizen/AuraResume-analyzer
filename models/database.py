import os
import json
import logging
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
from app.config import MONGODB_URI, DB_NAME, MOCK_DB_PATH, ALLOW_DB_FALLBACK

logger = logging.getLogger("resume_analyzer.database")

# DB State
db_client = None
db_collection = None
is_mongo_active = False

# Local mock database cache for fallback mode
mock_db_cache = {}

def load_mock_db() -> Dict[str, Any]:
    global mock_db_cache
    if os.path.exists(MOCK_DB_PATH):
        try:
            with open(MOCK_DB_PATH, "r", encoding="utf-8") as f:
                mock_db_cache = json.load(f)
                return mock_db_cache
        except Exception as e:
            logger.error(f"Error loading mock database file: {e}")
    mock_db_cache = {}
    return mock_db_cache

def save_mock_db() -> None:
    try:
        with open(MOCK_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(mock_db_cache, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving mock database file: {e}")

async def init_db() -> bool:
    global db_client, db_collection, is_mongo_active
    
    # Pre-load local JSON db in case we need it
    load_mock_db()
    
    if not MONGODB_URI:
        logger.info("MongoDB URI not provided. Using JSON database fallback.")
        is_mongo_active = False
        return False
        
    try:
        logger.info(f"Attempting to connect to MongoDB: {MONGODB_URI}")
        # Set a short timeout (2.5 seconds) for server selection so we don't hang if Mongo isn't running
        db_client = AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=2500)
        
        # Trigger connection check
        await db_client.admin.command('ping')
        
        db = db_client[DB_NAME]
        db_collection = db["reports"]
        is_mongo_active = True
        logger.info("Successfully connected to MongoDB!")
        return True
    except (ServerSelectionTimeoutError, Exception) as e:
        logger.warning(f"Failed to connect to MongoDB: {e}. Falling back to JSON database.")
        is_mongo_active = False
        db_client = None
        db_collection = None
        return False

async def save_report(report_id: str, report_data: Dict[str, Any]) -> bool:
    global is_mongo_active, db_collection
    
    if is_mongo_active and db_collection is not None:
        try:
            # Insert or replace report
            await db_collection.replace_one({"id": report_id}, report_data, upsert=True)
            return True
        except Exception as e:
            logger.error(f"MongoDB save failed: {e}. Falling back to saving locally.")
            # Fallback to local file on Mongo failure
            
    # Save to local mock JSON db
    mock_db_cache[report_id] = report_data
    save_mock_db()
    return True

async def get_report(report_id: str) -> Optional[Dict[str, Any]]:
    global is_mongo_active, db_collection
    
    if is_mongo_active and db_collection is not None:
        try:
            report = await db_collection.find_one({"id": report_id})
            if report:
                # Remove MongoDB _id field if exists
                if "_id" in report:
                    del report["_id"]
                return report
        except Exception as e:
            logger.error(f"MongoDB query failed: {e}. Falling back to local cache.")
            
    # Read from local mock JSON db
    load_mock_db() # Reload to ensure freshness
    return mock_db_cache.get(report_id)
