# config.py

from dotenv import load_dotenv
import os

# 1. Load the .env file FIRST. Every module that needs config imports this.
load_dotenv()

# 2. Define a function to safely retrieve and validate settings
def get_setting(key: str, default: str) -> str:
    """Retrieves environment variable or uses a safe default."""
    value = os.getenv(key)
    
    # Check if the variable is missing or is the literal string 'None'
    if value is None or value.strip().lower() == 'none':
        # print(f"DEBUG: Using default for {key}: {default}")
        return default
    
    # Strip any trailing whitespace/newlines that cause errors
    return value.strip()

# 3. Define all application settings using the safe retrieval function
# --- Database Settings ---
POSTGRES_USER = get_setting('POSTGRES_USER', 'user')
POSTGRES_PASSWORD = get_setting('POSTGRES_PASSWORD', 'password')
POSTGRES_HOST = get_setting('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = get_setting('POSTGRES_PORT', '5432') # The key line with a fallback!
POSTGRES_DB = get_setting('POSTGRES_DB', 'ai_db')

# --- AI Settings ---
OPENAI_API_KEY = get_setting('OPENAI_API_KEY', 'MOCK_KEY')

# --- Other Settings ---
BACKEND_PORT = int(get_setting('BACKEND_PORT', '8000')) # Safe to cast here now