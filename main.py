# main.py 
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Union
from datetime import datetime
import os
import uuid
import openai
from openai import OpenAI
from openai import APIError 
from database import Prompt, get_db
import config 


OPENAI_API_KEY = config.OPENAI_API_KEY


try:
    openai_client = None
    if OPENAI_API_KEY and OPENAI_API_KEY != 'MOCK_KEY':
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    
    print(f"Warning: Failed to initialize OpenAI client. Key might be invalid. Error: {e}")

app = FastAPI()


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
    
   
    model_config = {'from_attributes': True}



def generate_llm_response(query: str) -> Dict[str, str]:
    """Generates dual-tone responses using the LLM client and optimized prompt engineering."""
    
    if not openai_client:
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Client not initialized. OPENAI_API_KEY is missing or invalid."
        )
    
    
    casual_prompt = (
        f"**ROLE:** You are a seasoned tech blogger and social media personality. **TONE:** Enthusiastic, engaging, and extremely easy to understand. Use analogies and modern language. "
        f"**TASK:** Explain the concept '{query}' in a fun, one-paragraph summary. "
        f"**FORMAT CONSTRAINT:** Limit the response to 4 sentences and include exactly one relevant emoji at the end."
    )

   
    formal_prompt = (
        f"**ROLE:** You are a senior university lecturer in the field related to the topic. **TONE:** Objective, authoritative, and analytical. Use professional terminology. "
        f"**TASK:** Provide a concise, academic explanation of '{query}'. "
        f"**FORMAT CONSTRAINT:** Structure the response into three distinct, short sections: 1. Definition and Context, 2. Key Mechanisms/Components, and 3. Significance/Implications."
    )

    try:
    
        casual_response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": casual_prompt}]
        ).choices[0].message.content

      
        formal_response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": formal_prompt}]
        ).choices[0].message.content
        
        return {
            "casual_response": casual_response,
            "formal_response": formal_response
        }

    except openai.APIError as e:
        print(f"OpenAI API Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"External AI Service Error: {e.code} ({e.type}). Check key and rate limits."
        )
    except Exception as e:
        
        print(f"LLM API Call Failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="LLM Generation Failed due to unexpected error."
        )



@app.post("/generate", response_model=GenerateResponse)
def generate_content(request: GenerateRequest, db: Session = Depends(get_db)):
    """Handles content generation and saves the result to the database."""
    
    
    ai_responses = generate_llm_response(request.query)

    
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
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database Save Failed: {e}"
        )

    
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
      
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database Query Failed: {e}"
        )
        
    return history
