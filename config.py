import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
MOCK_DB_DIR = os.path.join(BASE_DIR, "reports")

# Ensure required directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MOCK_DB_DIR, exist_ok=True)

# Configuration Variables
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")

# API Keys and Connections
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "resume_analyzer")

# Allow mock database fallback if MongoDB connection fails or is not provided
ALLOW_DB_FALLBACK = True
MOCK_DB_PATH = os.path.join(MOCK_DB_DIR, "mock_db.json")
