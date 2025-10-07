# app.py
import streamlit as st
import requests
import json
import time # For loading spinner

# Define the user ID mock (Authentication mock bonus) [cite: 49]
MOCK_USER_ID = "ai_intern_user_123"
BACKEND_URL = "http://localhost:8000"# Change if your backend runs elsewhere

st.set_page_config(page_title="AI Dual-Tone Generator")
st.title("🤖 AI Response Generator")

# --- History Sidebar (Collapsible) [cite: 44] ---
# Function to fetch history
def fetch_history(user_id):
    try:
        response = requests.get(f"{BACKEND_URL}/history?user_id={user_id}")
        response.raise_for_status() # Raises an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to backend: {e}")
        return []

st.sidebar.header("Past Interactions")
history = fetch_history(MOCK_USER_ID)

if history:
    for item in history:
        with st.sidebar.expander(f"Query: {item['query'][:30]}..."):
            st.caption(f"Time: {item['created_at'].split('.')[0]}")
            st.markdown(f"**Casual:** {item['casual_response'][:100]}...")
            st.markdown(f"**Formal:** {item['formal_response'][:100]}...")
else:
    st.sidebar.info("No history found for this user.")

st.divider()

# --- Main Interaction Form [cite: 40, 41, 42] ---
st.header("New Query")
query_input = st.text_area("Enter your topic or question:", placeholder="e.g., Explain the theory of relativity")

if st.button("Generate Responses"):
    if not query_input:
        st.error("Please enter a query.")
    else:
        # Prepare the request payload
        payload = {
            "user_id": MOCK_USER_ID,
            "query": query_input
        }
        
        # Display loading spinner (Bonus feature) [cite: 50]
        with st.spinner("Generating AI responses..."):
            try:
                # POST request to the FastAPI microservice
                response = requests.post(f"{BACKEND_URL}/generate", json=payload)
                response.raise_for_status()
                result = response.json()
                
                # Store the result in session state for display persistence
                st.session_state['last_result'] = result
                st.session_state['last_query'] = query_input

            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred: {e}")
                st.session_state['last_result'] = None
                
        # Re-run the app to update the history sidebar and display results
        st.rerun() 

# --- Display Results [cite: 43] ---
if 'last_result' in st.session_state and st.session_state['last_result']:
    st.subheader(f"Responses for: *{st.session_state['last_query']}*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("🎉 Casual/Creative Style")
        st.markdown(st.session_state['last_result']['casual_response'])
        
    with col2:
        st.info("🏛️ Formal/Analytical Style")
        st.markdown(st.session_state['last_result']['formal_response'])