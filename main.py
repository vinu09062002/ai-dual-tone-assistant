# main.py - FINAL PRODUCTION VERSION
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
import os
import uuid
import openai # Assuming you are using the OpenAI API
from openai import OpenAI # Use this for the official client

# Project Modules
from database import Prompt, get_db
import config # Contains the OPENAI_API_KEY setting

# --- 1. CONFIGURATION & APP INITIALIZATION ---

# Get LLM API Key securely from the config module
OPENAI_API_KEY = config.OPENAI_API_KEY

# Initialize the OpenAI client globally
# It will use the key read from the environment via the config module
try:
    if OPENAI_API_KEY and OPENAI_API_KEY != 'MOCK_KEY':
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
    else:
        openai_client = None
except Exception as e:
    print(f"Warning: Failed to initialize OpenAI client. Key might be invalid. Error: {e}")
    openai_client = None

app = FastAPI()

# --- 2. Pydantic Models ---

class GenerateRequest(BaseModel):
    user_id: str
    query: str

class GenerateResponse(BaseModel):
    casual_response: str
    formal_response: str

class HistoryItem(GenerateResponse):
    user_id: str
    query: str
    created_at: datetime
    
    # Configuration to allow mapping from SQLAlchemy ORM objects
    model_config = {'from_attributes': True}

# --- 3. AI GENERATION LOGIC (Real Implementation) ---

def generate_llm_response(query: str) -> Dict[str, str]:
    """Generates dual-tone responses using the LLM client and prompt engineering."""
    
    if not openai_client:
        # Fallback if the key failed initialization
        return {
            "casual_response": f"MOCK FAILURE: AI Client not initialized. Check OPENAI_API_KEY.",
            "formal_response": f"MOCK FAILURE: AI Client not initialized. Check OPENAI_API_KEY."
        }
    
    # --- Prompt Engineering: Define the two styles ---
    casual_prompt = (
        f"You are a fun, friendly expert. Explain '{query}' in a creative, casual, "
        "and easy-to-understand summary. Keep it brief and engaging."
    )
    formal_prompt = (
        f"You are a strict, academic expert. Provide a formal, analytical, and structured "
        f"explanation of '{query}'. Use high-level language and clear paragraphs."
    )

    try:
        # 1. Generate Casual Response
        casual_response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": casual_prompt}]
        ).choices[0].message.content

        # 2. Generate Formal Response
        formal_response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role
