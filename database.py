# database.py - Final Hardened Version
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

# --- CORE LOGIC: Inject the default port if missing ---

def format_database_url(raw_url: str) -> str:
    """Ensures the URL contains the default port to prevent SQLAlchemy errors."""
    
    # 1. Check if the URL is missing the port part
    if "@" in raw_url and raw_url.count(':') < 3: # Simple check for missing port segment
        
        # Parse the URL components
        url_object = urlparse(raw_url)
        
        # If the port is genuinely missing, enforce the default PostgreSQL port (5432)
        if not url_object.port:
            
            # Reconstruct the netloc (host and port) manually
            new_netloc = f"{url_object.netloc.split('@')[0]}@{url_object.hostname}:5432"
            
            # Reconstruct the entire URL string
            final_url = url_object._replace(netloc=new_netloc).geturl()
            print(f"DEBUG: Injected default port 5432 into URL.")
            return final_url
    
    return raw_url

# --- ENVIRONMENT VARIABLE SETUP ---
# ... (rest of your database.py should use the same retrieval logic) ...

def get_database_url() -> str:
    """Retrieves the database URL, prioritizing the full environment secret."""
    db_base64 = os.getenv("DB_URL_BASE64")
    db_url = None
    
    if db_base64:
        try:
            # Decode the URL string (your fix for intermittent 'None' issue)
            db_url = base64.b64decode(db_base64).decode('utf-8').strip()
        except Exception:
            pass
            
    # Fallback to the standard (and potentially problematic) DATABASE_URL
    if not db_url:
        db_url = os.getenv("DATABASE_URL")
        
    return db_url if db_url else "" # Return empty string if truly missing

# --- EXECUTION ---
RAW_DATABASE_URL = get_database_url()

if not RAW_DATABASE_URL:
    sys.exit("FATAL ERROR: DB connection secret is missing. Check Render settings.")

# Inject the port here to solve the ValueError
DATABASE_URL = format_database_url(RAW_DATABASE_URL) 

# --- SQLAlchemy Setup ---
# (Rest of your SQLAlchemy setup remains the same, using the new DATABASE_URL)
# ...
Engine = create_engine(
    DATABASE_URL, 
    # Use the specific connect_args you defined previously:
    connect_args={
        "sslmode": "require"
    }
)
# ... rest of the file ...

# --- SQLAlchemy Setup ---
Engine = create_engine(
    DATABASE_URL, 
    # Add connect_args to force SSL/TLS connection, which is often required by Render.
    connect_args={
        "sslmode": "require"
    }
)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)

# --- Database Schema (omitted for brevity, keep your existing schema) ---

# --- Database Utility Functions (omitted for brevity, keep your existing functions) ---

class Prompt(Base):
    __tablename__ = "prompts"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    query = Column(Text)
    casual_response = Column(Text)
    formal_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

def create_db_and_tables():
    Base.metadata.create_all(bind=Engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
