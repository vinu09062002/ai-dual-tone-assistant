# database.py - Hardened for Render Deployment
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid
import os
import sys
import urllib.parse
from urllib.parse import urlparse

# --- CRITICAL ENVIRONMENT VARIABLE SETUP ---
# In a robust deployment, the only variable needed here is the full URL.
DATABASE_URL = os.getenv("DATABASE_URL")

# 1. VALIDATION CHECK: If the variable is missing, crash immediately.
if not DATABASE_URL:
    # Use sys.exit to stop the startup process clearly.
    sys.exit("FATAL ERROR: The DATABASE_URL environment variable is missing. Check Render settings.")


# 2. SSL FIX: Ensure SQLAlchemy connects securely to Render Postgres.
if DATABASE_URL.startswith("postgresql://"):
    # SQLAlchemy requires an SSL mode for remote PostgreSQL.
    # We will try to update the scheme to ensure psycopg2 is used and enforce SSL.
    try:
        # Parse the URL to safely handle the password encoding.
        url_object = urlparse(DATABASE_URL)
        password_encoded = urllib.parse.quote_plus(url_object.password)
        
        # Reconstruct the URL with the psycopg2 driver and the encoded password
        # This addresses potential character issues in the password.
        DATABASE_URL = f"postgresql+psycopg2://{url_object.username}:{password_encoded}@{url_object.hostname}:{url_object.port}/{url_object.path.lstrip('/')}"
        
    except Exception as e:
        # Fallback if parsing fails, but raise a clear error if needed
        print(f"Warning: Could not safely parse URL components. Error: {e}")


# --- SQLAlchemy Setup ---
# Engine creation is now guaranteed to receive a valid string.
Engine = create_engine(
    DATABASE_URL, 
    # Add connect_args to force SSL/TLS connection, which is often required by Render.
    connect_args={
        "sslmode": "require"
    }
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
# Function to create tables (run via Start Command)
def create_db_and_tables():
    Base.metadata.create_all(bind=Engine)

# Dependency to get a DB session (used by FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
