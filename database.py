# database.py
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid
import os
import urllib.parse
# Note: We do NOT use dotenv here, as cloud environments (Render) set variables directly.

# --- CRITICAL ENVIRONMENT VARIABLE SETUP ---

# 1. Read the full DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. VALIDATION CHECK: If the variable is missing, crash immediately with a clear message.
# This prevents low-level SQLAlchemy/psycopg2 errors that result in generic 500s.
if not DATABASE_URL:
    raise EnvironmentError(
        "FATAL ERROR: The DATABASE_URL environment variable is missing. "
        "Please ensure it is set correctly in your Render Web Service settings."
    )

# --- POSTGRESQL SSL FIX ---
# Render Postgres requires SSL to be explicitly enforced. 
# We parse the URL to determine if we need to set the SSL mode.

# SQLAlchemy uses 'postgresql' or 'postgres' dialect.
# The URL must be slightly modified if using psycopg2 with SSL requirements.
# The `url` is parsed to remove "postgresql://" and prepend "postgresql+psycopg2://" 
# if needed, but modern SQLAlchemy handles this well if we pass connect_args.

if DATABASE_URL.startswith("postgresql://"):
    # Change the scheme for Render/psycopg2 to enforce SSL
    # This ensures the client knows to use the secure connection method.
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
    
    # We must URL-encode the password to handle any special characters, 
    # even the '@' in the password itself (if present), before passing to the engine.
    try:
        # Simple parsing to get the password out and encode it
        url_parts = urllib.parse.urlparse(DATABASE_URL)
        password_encoded = urllib.parse.quote_plus(url_parts.password)
        
        # Reconstruct the URL with the encoded password
        DATABASE_URL = url_parts._replace(
            netloc=f"{url_parts.username}:{password_encoded}@{url_parts.hostname}:{url_parts.port}"
        ).geturl()
        
    except Exception as e:
        # If parsing fails, use the original URL but we need to proceed with SSL connect_args
        print(f"Warning: Could not safely encode password in URL. Error: {e}")


# --- SQLAlchemy Setup ---
# Add connect_args to force SSL/TLS connection, which is often required by Render Postgres.
Engine = create_engine(
    DATABASE_URL, 
    # This is the standard way to enforce SSL for external Postgres connections
    connect_args={
        "sslmode": "require"
    }
)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)

# --- Database Schema ---
class Prompt(Base):
    __tablename__ = "prompts"
    
    # Using String(36) is sufficient and clean for storing UUIDs as text.
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    user_id = Column(String, index=True)
    query = Column(Text)
    casual_response = Column(Text)
    formal_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# --- Database Utility Functions ---
# Function to create tables (run this once)
def create_db_and_tables():
    # Use checkfirst=True (the default) to prevent errors if tables already exist.
    Base.metadata.create_all(bind=Engine)

# Dependency to get a DB session (used by FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
