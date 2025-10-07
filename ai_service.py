# ai_service.py
import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

CASUAL_PROMPT_TEMPLATE = """
Act as a fun, creative, and casual social media commentator. 
Explain the following topic in a short, easy-to-digest summary 
that uses simple language and an energetic tone: 
"{query}"
"""

FORMAL_PROMPT_TEMPLATE = """
Act as a formal, analytical academic researcher. 
Provide a detailed, objective, and structured explanation 
of the following topic, citing key concepts and using 
professional terminology: 
"{query}"
"""

# For mocking, in case API access is unavailable [cite: 21]
def generate_ai_responses(query: str):
    # Temporarily return mock responses, ignoring API call
    print("DEBUG: Using mock AI responses to isolate error.")
    return {
        "casual_response": f"MOCK: Casual summary for {query}",
        "formal_response": f"MOCK: Formal analysis for {query}",
    }

#def generate_ai_responses(query: str):
    if not openai.api_key:
        # Fallback to mock if key isn't set
        return mock_ai_responses(query) 

    # --- 1. Casual/Creative Response ---
    casual_prompt = CASUAL_PROMPT_TEMPLATE.format(query=query)
    casual_completion = openai.Completion.create(
        model="text-davinci-003", # or gpt-3.5-turbo via ChatCompletion
        prompt=casual_prompt,
        max_tokens=250,
        temperature=0.8 
    )
    casual_response = casual_completion.choices[0].text.strip()

    # --- 2. Formal/Analytical Response ---
    formal_prompt = FORMAL_PROMPT_TEMPLATE.format(query=query)
    formal_completion = openai.Completion.create(
        model="text-davinci-003",
        prompt=formal_prompt,
        max_tokens=350,
        temperature=0.3 # Lower temperature for more factual/less creative
    )
    formal_response = formal_completion.choices[0].text.strip()

    return {
        "casual_response": casual_response,
        "formal_response": formal_response,
    }

# Update the placeholder in main.py to import and use this function.