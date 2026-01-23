import streamlit as st
import sys
from pathlib import Path
import requests
import time
from datetime import datetime
import os

# -------------------------------
# Setup PYTHONPATH
# -------------------------------
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from ui.components.utils import normalize_intent, CUSTOM_CSS
from ui.components.sidebar import render_sidebar, render_metrics
from ui.components.chat import render_chat_history

# -------------------------------
# Backend API URL
# -------------------------------
API_URL = os.getenv("API_URL", "http://localhost:8070/query")

# -------------------------------
# Page Config & Custom CSS
# -------------------------------
st.set_page_config(
    page_title="Agentic Customer Support AI",
    layout="wide",
    page_icon="🤖",
    initial_sidebar_state="expanded"
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -------------------------------
# Session State Initialization
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = "ui-thread-001"

# -------------------------------
# Sidebar
# -------------------------------
render_sidebar()

# -------------------------------
# Main Content
# -------------------------------
# Header with gradient
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            margin-bottom: 2rem;">
    <h1 style="margin:0; color:white;">🤖 Agentic Customer Support AI</h1>
    <p style="margin:0.5rem 0 0 0; opacity:0.9;">
        LangGraph • RAG • Human-in-the-Loop • Persistent State
    </p>
</div>
""", unsafe_allow_html=True)

render_metrics(API_URL)

# -------------------------------
# Conversation History
# -------------------------------
render_chat_history()

# -------------------------------
# User Input Section
# -------------------------------
st.markdown("### 💬 Ask the Assistant")

# Using a form for better UX
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([4, 1])
    
    with col1:
        query = st.text_input(
            "Type your question here...",
            placeholder="e.g., What's your return policy for damaged items?",
            label_visibility="collapsed",
            key="query_input"
        )
    
    with col2:
        submit_button = st.form_submit_button(
            "🚀 Send",
            use_container_width=True,
            type="primary"
        )
    
    # Quick action buttons
    st.markdown("**💡 Quick Questions:**")
    quick_col1, quick_col2, quick_col3 = st.columns(3)
    
    with quick_col1:
        if st.form_submit_button("📦 Shipping Info", use_container_width=True):
            query = "What are your shipping options and delivery times?"
    
    with quick_col2:
        if st.form_submit_button("🔄 Returns", use_container_width=True):
            query = "What is your return policy for damaged items?"
    
    with quick_col3:
        if st.form_submit_button("💰 Pricing", use_container_width=True):
            query = "Do you offer any discounts or promotions?"

if submit_button and query:
    payload = {
        "query": query,
        "thread_id": st.session_state.thread_id,
    }

    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": query,
    })
    
    # Show progress and thinking animation
    with st.status("🤖 **Processing your request...**", expanded=True) as status:
        try:
            st.write("📡 Connecting to backend...")
            
            # Simulate processing steps
            processing_steps = [
                "🔍 Analyzing intent...",
                "📚 Searching knowledge base...",
                "🤔 Determining best response...",
                "✍️ Generating answer..."
            ]
            
            for step in processing_steps:
                time.sleep(0.3)  # Short delay for visual effect
                st.write(step)
            
            # Actual API call
            with st.spinner("Making API call..."):
                resp = requests.post(API_URL, json=payload, timeout=60)
            
            if resp.status_code != 200:
                status.update(label="❌ Backend error", state="error")
                st.error(f"Backend returned status code: {resp.status_code}")
                st.stop()
            
            result = resp.json()
            intent_info = normalize_intent(result.get("intent"))

            # -------------------------------
            # Escalation vs Normal Response
            # -------------------------------
            if result.get("escalate") is True:
                status.update(label="⚠️ Human intervention required", state="error")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "⚠️ This issue has been escalated to a human support agent.",
                    "meta": {
                        "intent": intent_info,
                        "decision": result.get("decision"),
                    },
                })

                st.rerun()

            else:
                assistant_text = result.get("final_answer")
                if not assistant_text:
                    assistant_text = "⚠️ No response generated."

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_text,
                    "meta": {
                        "intent": intent_info,
                        "decision": result.get("decision"),
                        "sources": result.get("sources"),
                        "confidence": result.get("confidence", "N/A"),
                    },
                })

                status.update(label="✅ Response generated!", state="complete")
                st.rerun()
        except Exception as e:
            status.update(label="❌ Error", state="error")
            st.error(f"An error occurred while processing your request: {e}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": "⚠️ An error occurred while processing your request.",
                "meta": {"error": str(e)},
            })
            # Re-raise or stop to avoid inconsistent state; use st.rerun to refresh UI
            st.rerun()


# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.caption("🔄 Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

with col2:
    st.caption("📊 Messages processed: " + str(len(st.session_state.get("messages", []))))

with col3:
    st.caption("🤖 Powered by LangGraph & RAG")

# Scroll to bottom button
st.markdown("""
<div style="text-align: center; margin-top: 2rem;">
    <button onclick="window.scrollTo(0, document.body.scrollHeight);" 
            style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 20px; 
                   padding: 0.5rem 1.5rem; color: #6c757d; cursor: pointer;">
        ⬇️ Scroll to Bottom
    </button>
</div>
""", unsafe_allow_html=True)
