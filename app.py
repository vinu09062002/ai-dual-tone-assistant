# streamlit_app.py
import streamlit as st
import requests
import os
import json
import time 


MOCK_USER_ID = "ai_intern_user_123"


try:
    BACKEND_URL = st.secrets["backend_url"]
except KeyError:
    BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
    st.warning("Using local/default backend URL. Set 'backend_url' in Streamlit Secrets for cloud deployment.")

st.set_page_config(page_title="AI Dual-Tone Generator")
st.title("🤖 AI Response Generator")


def fetch_history(user_id):
    try:
        response = requests.get(f"{BACKEND_URL}/history?user_id={user_id}", timeout=30)
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.RequestException as e:
        st.sidebar.error(f"History connection error: {e}")
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


st.header("New Query")
query_input = st.text_area("Enter your topic or question:", placeholder="e.g., Explain the theory of relativity")


if st.button("Generate Responses"):
    if not query_input:
        st.error("Please enter a query.")
    else:
       
        payload = {
            "user_id": MOCK_USER_ID,
            "query": query_input
        }
        
        
        with st.spinner("Generating AI responses..."):
            try:
                
                response = requests.post(f"{BACKEND_URL}/generate", json=payload, timeout=60)
                response.raise_for_status()
                result = response.json()
                
               
                st.session_state['last_result'] = result
                st.session_state['last_query'] = query_input

            except requests.exceptions.RequestException as e:
               
                st.error(f"Error connecting to backend: Please check the Render Web Service logs. Details: {e}")
                st.session_state['last_result'] = None 
                
       
        st.rerun() 


if 'last_result' in st.session_state and st.session_state['last_result']:
    st.subheader(f"Responses for: *{st.session_state['last_query']}*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("🎉 Casual/Creative Style")
        st.markdown(st.session_state['last_result']['casual_response'])
        
    with col2:
        st.info("🏛️ Formal/Analytical Style")
        st.markdown(st.session_state['last_result']['formal_response'])
