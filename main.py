# main.py - FINAL PRODUCTION VERSION
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Union
from datetime import datetime
import os
import uuid
import openai
from openai import OpenAI
from openai import APIError # Import specific exception for better handling

# Project Modules
from database import Prompt, get_db
import config # Contains the OPENAI_API_KEY setting

# --- 1. CONFIGURATION & APP INITIALIZATION ---

# Get LLM API Key securely from the config module
OPENAI_API_KEY = config.OPENAI_API_KEY

# Initialize the OpenAI client globally
try:
    openai_client = None
    if OPENAI_API_KEY and OPENAI_API_KEY != 'MOCK_KEY':
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    # This warning will appear in Render logs during startup
    print(f"Warning: Failed to initialize OpenAI client. Key might be invalid. Error: {e}")

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
    """Generates dual-tone responses using the LLM client and optimized prompt engineering."""
    
    if not openai_client:
        # Fallback if the key failed initialization
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Client not initialized. OPENAI_API_KEY is missing or invalid."
        )
    
    # --- Prompt Engineering: Define the two distinct, optimized styles ---
    
    # Casual/Creative Prompt: Uses a persona, enthusiastic tone, and strict constraints.
    casual_prompt = (
        f"**ROLE:** You are a seasoned tech blogger and social media personality. **TONE:** Enthusiastic, engaging, and extremely easy to understand. Use analogies and modern language. "
        f"**TASK:** Explain the concept '{query}' in a fun, one-paragraph summary. "
        f"**FORMAT CONSTRAINT:** Limit the response to 4 sentences and include exactly one relevant emoji at the end."
    )

    # Formal/Analytical Prompt: Uses an academic persona and demands structured, formal output.
    formal_prompt = (
        f"**ROLE:** You are a senior university lecturer in the field related to the topic. **TONE:** Objective, authoritative, and analytical. Use professional terminology. "
        f"**TASK:** Provide a concise, academic explanation of '{query}'. "
        f"**FORMAT CONSTRAINT:** Structure the response into three distinct, short sections: 1. Definition and Context, 2. Key Mechanisms/Components, and 3. Significance/Implications."
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
            messages=[{"role": "user", "content": formal_prompt}]
        ).choices[0].message.content
        
        return {
            "casual_response": casual_response,
            "formal_response": formal_response
        }

    except openai.APIError as e:
        # Catch specific OpenAI errors (Authentication, Rate Limits, etc.)
        print(f"OpenAI API Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"External AI Service Error: {e.code} ({e.type}). Check key and rate limits."
        )
    except Exception as e:
        # Catch any other runtime error during the call (like network timeout)
        print(f"LLM API Call Failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="LLM Generation Failed due to unexpected error."
        )

# --- 4. API Endpoints ---

@app.post("/generate", response_model=GenerateResponse)
def generate_content(request: GenerateRequest, db: Session = Depends(get_db)):
    """Handles content generation and saves the result to the database."""
    
    # 1. Generate AI responses (will raise 500 HTTPException if it fails)
    ai_responses = generate_llm_response(request.query)

    # 2. Save interaction to Postgres
    try:
        db_prompt = Prompt(
            user_id=request.user_id,
            query=request.query,
            casual_response=ai_responses["casual_response"],
            formal_response=ai_responses["formal_response"]
        )
        db.add(db_prompt)
        db.commit()
        db.refresh(db_prompt)
    except Exception as e:
        db.rollback()
        # Catch database transactional errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database Save Failed: {e}"
        )

    # 3. Return responses
    return GenerateResponse(**ai_responses)


@app.get("/history", response_model=List[HistoryItem])
def get_history(user_id: str, db: Session = Depends(get_db)):
    """Retrieves all past interactions for the given user in reverse chronological order."""
    
    try:
        history = (
            db.query(Prompt)
            .filter(Prompt.user_id == user_id)
            .order_by(Prompt.created_at.desc()) 
            .all()
        )
    except Exception as e:
        # Catch database operational errors (like connection drops or missing tables)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database Query Failed: {e}"
        )
        
    return history
