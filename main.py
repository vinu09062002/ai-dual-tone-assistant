# main.py (initial part)
from fastapi import FastAPI
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from database import Prompt, get_db, create_db_and_tables
from ai_service import generate_ai_responses 
import config

# Run this function to set up the DB table
# create_db_and_tables() 

app = FastAPI()

# --- Pydantic Models ---
class GenerateRequest(BaseModel):
    user_id: str
    query: str

class GenerateResponse(BaseModel):
    casual_response: str
    formal_response: str

# main.py (Pydantic Models)
from datetime import datetime # <--- Ensure this is imported

# ... (other models) ...

class HistoryItem(GenerateResponse):
    user_id: str
    query: str
    created_at: datetime # <--- Must be datetime object
    # Add optional Pydantic config to handle ORM objects
    class Config:
        orm_mode = True 
        # Note: For Pydantic v2, this should be: model_config = {'from_attributes': True}

# Placeholder for AI generation function
def generate_ai_responses(query: str):
    # This will be replaced by the actual AI call in the next step
    # Mock responses for API structure test
    return {
        "casual_response": f"Hey, {query} is a cool thing!",
        "formal_response": f"Analysis of {query} suggests a formal explanation is required.",
    }

@app.post("/generate", response_model=GenerateResponse)
def generate_content(request: GenerateRequest, db: Session = Depends(get_db)):
    # 1. Generate AI responses
    ai_responses = generate_ai_responses(request.query)

    # 2. Save interaction to Postgres
    db_prompt = Prompt(
        user_id=request.user_id,
        query=request.query,
        casual_response=ai_responses["casual_response"],
        formal_response=ai_responses["formal_response"]
    )
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)

    # 3. Return responses
    return GenerateResponse(**ai_responses)

# main.py (continued)

@app.get("/history", response_model=List[HistoryItem])
def get_history(user_id: str, db: Session = Depends(get_db)):
    # Retrieve all past interactions for the user, reverse chronological order
    history = (
        db.query(Prompt)
        .filter(Prompt.user_id == user_id)
        .order_by(Prompt.created_at.desc()) # <--- Ordering field must exist
        .all()
    )
    # The return should work if orm_mode=True is set on the Pydantic model
    return history 

