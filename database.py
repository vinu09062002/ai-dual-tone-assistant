# database.py
from sqlalchemy import create_engine, Column, String, Text, DateTime
# Import the UUID type and make sure to use it for the ID column
from sqlalchemy.dialects.postgresql import UUID 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid
import os

# --- CRITICAL FIX: Use the single, complete DATABASE_URL environment variable ---

# 1. Ensure the required environment variable is present.
# In a cloud environment (Render), variables are set before code runs.
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. VALIDATION CHECK: If the variable is missing, crash with a clear message.
# This prevents the silent 'None' value from crashing the SQLAlchemy parser.
if not DATABASE_URL:
    raise EnvironmentError(
        "FATAL ERROR: The DATABASE_URL environment variable is missing. "
        "Please ensure it is set correctly in the Render Web Service settings."
    )

# --- SQLAlchemy Setup ---
# Engine creation is now guaranteed to receive a valid string.
# Ensure asyncpg is installed if you are using an async framework like FastAPI.
Engine = create_engine(DATABASE_URL) 
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)

# --- Database Schema ---
class Prompt(Base):
    __tablename__ = "prompts"
    
    # Updated ID to use UUID type (or String(36) if using sqlite/other dbs)
    # Since you specified PostgreSQL, using UUID is idiomatic.
    # The default creates a new UUID and converts it to a string for storage.
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    user_id = Column(String, index=True)
    query = Column(Text)
    casual_response = Column(Text)
    formal_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# --- Database Utility Functions ---
# Function to create tables (run this once)
def create_db_and_tables():
    Base.metadata.create_all(bind=Engine)

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
