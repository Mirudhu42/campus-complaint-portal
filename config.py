import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'campus-complaint-portal-super-secret-key-2026')
    
    # Database Configuration
    DB_ENGINE = os.environ.get('DB_ENGINE', 'mysql').lower() # 'mysql' or 'sqlite'
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'campus_complaint_portal')
    
    # SQLite file path if SQLite is used for local tests or fallback
    SQLITE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'campus_complaint_portal.sqlite')
    
    # Session Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400 # 24 hours
