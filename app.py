# streamlit_app.py
import streamlit as st
import requests
import os
import json
import time 

# --- CONFIGURATION ---
# Define the user ID mock (Authentication mock bonus)
MOCK_USER_ID = "ai_intern_user_123"

# --- DEPLOYMENT FIX: Read URL from Streamlit Secrets ---
# Use st.secrets to securely get the URL set in the Streamlit Cloud dashboard
try:
    # This key must match the key you set in the Streamlit Cloud secrets.toml file
    BACKEND_URL = st.secrets["backend_url"]
except KeyError:
    # Fallback for local testing. Use the environment variable if defined, 
    # otherwise default to the localhost address.
    BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
    st.warning("Using local/default backend URL. Set 'backend_url' in Streamlit Secrets for cloud deployment.")

st.set_page_config(page_title="AI Dual-Tone Generator")
st.title("🤖 AI Response Generator")

# --- Function to fetch history (GET /history) ---
def fetch_history(user_id):
    try:
        # Use the securely read BACKEND_URL
        response = requests.get(f"{BACKEND_URL}/history?user_id={user_id}", timeout=30)
        response.raise_for_status() # Raises an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        # Displaying error in the main panel if history fails to load
        st.sidebar.error(f"History connection error: {e}")
        return []

# --- History Sidebar (Collapsible) ---
st.sidebar.header("Past Interactions")
history = fetch_history(MOCK_USER_ID)

if history:
    for item in history:
        # Note: History items are returned in reverse chronological order
        with st.sidebar.expander(f"Query: {item['query'][:30]}..."):
            st.caption(f"Time: {item['created_at'].split('.')[0]}")
            st.markdown(f"**Casual:** {item['casual_response'][:100]}...")
            st.markdown(f"**Formal:** {item['formal_response'][:100]}...")
else:
    st.sidebar.info("No history found for this user.")

st.divider()

# --- Main Interaction Form ---
st.header("New Query")
query_input = st.text_area("Enter your topic or question:", placeholder="e.g., Explain the theory of relativity")

# Form validation check for non-empty input
if st.button("Generate Responses"):
    if not query_input:
        st.error("Please enter a query.")
    else:
        # Prepare the request payload
        payload = {
            "user_id": MOCK_USER_ID,
            "query": query_input
        }
        
        # Display loading spinner (Bonus feature)
        with st.spinner("Generating AI responses..."):
            try:
                # POST request to the FastAPI microservice
                # Use the securely read BACKEND_URL
                response = requests.post(f"{BACKEND_URL}/generate", json=payload, timeout=60)
                response.raise_for_status()
                result = response.json()
                
                # Store the result in session state for display persistence
                st.session_state['last_result'] = result
                st.session_state['last_query'] = query_input

            except requests.exceptions.RequestException as e:
                # Clearer error handling for the user
                st.error(f"Error connecting to backend: Please check the Render Web Service logs. Details: {e}")
                st.session_state['last_result'] = None # Use Python None for clarity
                
        # Re-run the app to update the history sidebar and display results
        st.rerun() 

# --- Display Results ---
# Check if the last_result is valid before attempting to display
if 'last_result' in st.session_state and st.session_state['last_result']:
    st.subheader(f"Responses for: *{st.session_state['last_query']}*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("🎉 Casual/Creative Style")
        st.markdown(st.session_state['last_result']['casual_response'])
        
    with col2:
        st.info("🏛️ Formal/Analytical Style")
        st.markdown(st.session_state['last_result']['formal_response'])
