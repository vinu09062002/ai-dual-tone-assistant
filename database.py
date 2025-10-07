# database.py
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid
import os
# from dotenv import load_dotenv # Only needed for local testing, commented out for clean cloud deploy
# from urllib.parse import quote_plus # Not needed if using the full DATABASE_URL secret

# --- CRITICAL FIX: Use the single, complete DATABASE_URL environment variable ---

# 1. Ensure the required environment variable is present.
# In a cloud environment (Render/Koyeb), variables are set before code runs.
# We will use the full URL provided by Render directly.
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. VALIDATION CHECK: If the variable is missing, crash with a clear message.
# This prevents the silent 'None' value from crashing the SQLAlchemy parser.
if not DATABASE_URL:
    raise EnvironmentError(
        "FATAL ERROR: The DATABASE_URL environment variable is missing. "
        "Please ensure it is set correctly in the Render/Koyeb Web Service settings."
    )

# --- SQLAlchemy Setup ---
# Engine creation is now guaranteed to receive a valid string.
Engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)

# --- Database Schema ---
class Prompt(Base):
    __tablename__ = "prompts"
    # Using String for UUIDs as required by the schema suggestion (page 1)
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
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
