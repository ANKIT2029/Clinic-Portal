import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = os.getenv("DB_NAME", "clinic_portal")
    DB_USER = os.getenv("DB_USER", "clinic_app")
    DB_PASS = os.getenv("DB_PASS", "change_this_password")
    
    # Server Configuration
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    HOST = "0.0.0.0"
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Frontend
    FRONTEND_FOLDER = os.path.join(os.path.dirname(__file__), "frontend")