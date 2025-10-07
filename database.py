# database.py - The Ultimate Fix
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid
import os
import sys
import base64
import urllib.parse
from urllib.parse import urlparse
from typing import Optional

# --- CRITICAL ENVIRONMENT VARIABLE SETUP ---

def get_database_url() -> Optional[str]:
    """Retrieves the database URL, prioritizing the full environment secret."""
    
    # 1. Try to read the Base64 encoded URL
    db_base64 = os.getenv("DB_URL_BASE64")
    if db_base64:
        try:
            # Decode the URL string
            decoded_url = base64.b64decode(db_base64).decode('utf-8')
            return decoded_url.strip()
        except Exception:
            # Fallback if decoding fails
            pass
            
    # 2. Fallback to the standard (potentially empty) DATABASE_URL
    return os.getenv("DATABASE_URL")

DATABASE_URL = get_database_url()

# 3. VALIDATION CHECK: If the URL is still missing, crash.
if not DATABASE_URL:
    # Use sys.exit to stop the startup process clearly.
    sys.exit("FATAL ERROR: DB connection secret is missing. Check Render settings for DB_URL_BASE64.")


# --- POSTGRESQL SSL FIX ---
# (Keep the SSL fix, as the connection still needs to be secure)

if DATABASE_URL.startswith("postgresql://"):
    # Reconstruct the URL for psycopg2 and handle password encoding
    try:
        url_object = urlparse(DATABASE_URL)
        password_encoded = urllib.parse.quote_plus(url_object.password)
        DATABASE_URL = f"postgresql+psycopg2://{url_object.username}:{password_encoded}@{url_object.hostname}:{url_object.port}/{url_object.path.lstrip('/')}"
        
    except Exception as e:
        print(f"Warning: URL parsing failed. Proceeding with original URL. Error: {e}")


# --- SQLAlchemy Setup ---
Engine = create_engine(
    DATABASE_URL, 
    connect_args={"sslmode": "require"}
)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)

# --- Database Schema ---
class Prompt(Base):
    __tablename__ = "prompts"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    query = Column(Text)
    casual_response = Column(Text)
    formal_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# --- Database Utility Functions ---
def create_db_and_tables():
    Base.metadata.create_all(bind=Engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
