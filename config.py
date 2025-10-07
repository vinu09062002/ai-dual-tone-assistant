# config.py

from dotenv import load_dotenv
import os

load_dotenv()

def get_setting(key: str, default: str) -> str:
    """Retrieves environment variable or uses a safe default."""
    value = os.getenv(key)
    
   
    if value is None or value.strip().lower() == 'none':
       
        return default
    
    
    return value.strip()

POSTGRES_USER = get_setting('POSTGRES_USER', 'user')
POSTGRES_PASSWORD = get_setting('POSTGRES_PASSWORD', 'password')
POSTGRES_HOST = get_setting('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = get_setting('POSTGRES_PORT', '5432') 
POSTGRES_DB = get_setting('POSTGRES_DB', 'ai_db')


OPENAI_API_KEY = get_setting('OPENAI_API_KEY', 'MOCK_KEY')


BACKEND_PORT = int(get_setting('BACKEND_PORT', '8000'))
