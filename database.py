# database.py
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid
from dotenv import load_dotenv
import os
import config # Import the settings module

# Construct the URL using the variables defined in config.py
DATABASE_URL = (
    f"postgresql://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@"
    f"{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB}"
)


# --- IMPORTANT ---
# 1. Ensure this is called first.
load_dotenv() 
# --- IMPORTANT ---

POSTGRES_PORT = os.getenv('POSTGRES_PORT')

from urllib.parse import quote_plus


# Ensure load_dotenv() is present and executes
load_dotenv() 

# Safely retrieve all variables
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432') 
POSTGRES_DB = os.getenv('POSTGRES_DB', 'ai_db')


# 🚨 CRITICAL FIX: URL-encode the password to handle the '@' symbol.
ENCODED_PASSWORD = quote_plus(POSTGRES_PASSWORD)

# Construct the URL using the encoded password
DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{ENCODED_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)


 # Load environment variables

DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}:{POSTGRES_PORT}/{os.getenv('POSTGRES_DB')}"
)

# Database connection string
DATABASE_URL = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)

Engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)

class Prompt(Base):
    __tablename__ = "prompts"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    query = Column(Text)
    casual_response = Column(Text)
    formal_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

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


