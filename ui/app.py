import streamlit as st
import sys
from pathlib import Path
import requests
import json
from datetime import datetime
import time

# -------------------------------
# Setup PYTHONPATH
# -------------------------------
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

# -------------------------------
# Backend API URL
# -------------------------------
API_URL = "http://localhost:8000/query"

# -------------------------------
# Helpers
# -------------------------------
def normalize_intent(intent):
    if intent is None:
        return None

    if hasattr(intent, "intent"):
        return {
            "label": intent.intent.value,
            "confidence": intent.confidence,
            "reason": intent.reason,
        }

    if hasattr(intent, "value"):
        return {
            "label": intent.value,
            "confidence": "N/A",
            "reason": "Rule-based routing",
        }

    if isinstance(intent, str):
        return {
            "label": intent,
            "confidence": "N/A",
            "reason": "Backend fallback",
        }

    return None

def get_intent_color(intent_label):
    """Return color based on intent type"""
    if not intent_label:
        return "#6c757d"
    
    intent_lower = intent_label.lower()
    if any(word in intent_lower for word in ["refund", "return", "cancel"]):
        return "#dc3545"  # Red
    elif any(word in intent_lower for word in ["shipping", "delivery", "track"]):
        return "#17a2b8"  # Teal
    elif any(word in intent_lower for word in ["product", "item", "stock"]):
        return "#28a745"  # Green
    elif any(word in intent_lower for word in ["account", "login", "password"]):
        return "#6f42c1"  # Purple
    elif any(word in intent_lower for word in ["pricing", "price", "discount"]):
        return "#fd7e14"  # Orange
    else:
        return "#007bff"  # Blue

# -------------------------------
# Page Config & Custom CSS
# -------------------------------
st.set_page_config(
    page_title="Agentic Customer Support AI",
    layout="wide",
    page_icon="🤖",
    initial_sidebar_state="expanded"
)
# -------------------------------
# Session State Initialization (FIX)
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = "ui-thread-001"

# Custom CSS for beautiful UI
st.markdown("""
<style>
    /* Main container styling */
    .main {
        padding: 1rem 2rem;
    }
    
    /* Custom button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.2);
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem 1rem;
    }
    
    /* Chat bubble styling */
    .user-bubble {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
        box-shadow: 0 4px 6px rgba(102, 126, 234, 0.1);
    }
    
    .assistant-bubble {
        background: #f8fafc;
        color: #2d3748;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 0.5rem 0;
        max-width: 80%;
        border-left: 4px solid #667eea;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.3s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Sidebar
# -------------------------------
with st.sidebar:
    st.title("⚙️ Settings")
    
    st.markdown("---")
    
    # Thread ID management
    st.markdown("### Thread Management")
    thread_id = st.text_input(
        "Conversation Thread ID",
        value=st.session_state.get("thread_id", "ui-thread-001"),
        help="Unique ID for this conversation thread"
    )
    st.session_state.thread_id = thread_id
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🆕 New Thread"):
            st.session_state.thread_id = f"thread-{int(time.time())}"
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    
    st.markdown("---")
    
    # System stats
    st.markdown("### 📊 Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Messages",
            len(st.session_state.get("messages", [])),
            delta=None
        )
    
    with col2:
        st.metric(
            "Thread ID",
            thread_id[-6:],
            delta=None
        )
    
    # Intent distribution (sample)
    st.markdown("### 🎯 Common Intents")
    intents = {
        "Refund/Return": get_intent_color("refund"),
        "Shipping": get_intent_color("shipping"),
        "Product Info": get_intent_color("product"),
        "Account": get_intent_color("account"),
        "Pricing": get_intent_color("pricing")
    }
    
    for intent_name, color in intents.items():
        st.markdown(
            f'<div style="background:{color}20; padding:0.5rem; '
            f'border-radius:5px; margin:0.25rem 0; border-left:3px solid {color}">'
            f'<span style="color:{color}; font-weight:600">●</span> {intent_name}'
            f'</div>',
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    st.caption("🔗 Connected to backend API")
    st.caption(f"📡 Endpoint: `{API_URL}`")

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

# Three-column layout for stats
col1, col2, col3 = st.columns(3)

with col1:
    with st.container():
        st.markdown('<div class="metric-card" style="border-left-color: #667eea;">', unsafe_allow_html=True)
        st.metric("Active Thread", st.session_state.thread_id.split('-')[-1])
        st.caption("Current conversation")
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    with st.container():
        st.markdown('<div class="metric-card" style="border-left-color: #28a745;">', unsafe_allow_html=True)
        total_msgs = len(st.session_state.get("messages", []))
        user_msgs = len([m for m in st.session_state.get("messages", []) if m["role"] == "user"])
        st.metric("Messages", total_msgs, delta=f"{user_msgs} from user")
        st.caption("Conversation volume")
        st.markdown('</div>', unsafe_allow_html=True)

with col3:
    with st.container():
        st.markdown('<div class="metric-card" style="border-left-color: #fd7e14;">', unsafe_allow_html=True)
        st.metric("API Status", "Connected" if API_URL else "Disconnected")
        st.caption("Backend connection")
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# -------------------------------
# Conversation History
# -------------------------------
st.markdown("### 💬 Conversation History")

# Check if conversation is empty
if not st.session_state.get("messages"):
    st.info("💭 No messages yet. Start a conversation below!")
else:
    # Display conversation with beautiful bubbles
    for i, msg in enumerate(st.session_state.messages):
        # Create columns for avatar and message
        col1, col2 = st.columns([1, 15])
        
        with col1:
            if msg["role"] == "user":
                st.markdown("""
                <div style="background: #667eea; color: white; width: 40px; height: 40px; 
                            border-radius: 50%; display: flex; align-items: center; 
                            justify-content: center; font-weight: bold; margin-top: 10px;">
                    👤
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: #10b981; color: white; width: 40px; height: 40px; 
                            border-radius: 50%; display: flex; align-items: center; 
                            justify-content: center; font-weight: bold; margin-top: 10px;">
                    🤖
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="user-bubble fade-in">
                    <div style="font-weight: 600; margin-bottom: 4px;">You</div>
                    <div>{msg["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="assistant-bubble fade-in">
                    <div style="font-weight: 600; margin-bottom: 4px;">Assistant</div>
                    <div>{msg["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Meta information expander with improved styling
                if msg.get("meta"):
                    with st.expander("🔍 **View Analysis Details**", expanded=False):
                        meta = msg["meta"]
                        
                        # Intent with colored tag
                        if meta.get("intent"):
                            intent_label = meta["intent"]["label"] if isinstance(meta["intent"], dict) else meta["intent"]
                            intent_color = get_intent_color(intent_label)                    
                            st.markdown(f"""
                            <div style="background: {intent_color}20; padding: 0.75rem; 
                                        border-radius: 8px; border-left: 4px solid {intent_color}; 
                                        margin-bottom: 1rem;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span style="color: {intent_color}; font-size: 1.2em;">•</span>
                                    <div>
                                        <div style="font-weight: 600; color: {intent_color};">
                                            {intent_label}
                                        </div>
                                        <div style="font-size: 0.9em; color: #6c757d;">
                                            Detected Intent
                                        </div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Confidence and reason in columns
                        if meta.get("confidence") or meta.get("reason"):
                            col_a, col_b = st.columns(2)
                            
                            with col_a:
                                if meta.get("confidence"):
                                    st.metric("Confidence Score", meta["confidence"])
                            
                            with col_b:
                                if meta.get("reason"):
                                    st.info(f"**Reason:** {meta['reason']}")
                        
                        # Decision
                        if meta.get("decision"):
                            st.success(f"**Decision Made:** {meta['decision']}")
                        
                        # Sources with copy button
                        if meta.get("sources"):
                            st.markdown("**📚 Sources Used:**")
                            if isinstance(meta["sources"], str):
                                # Add copy button
                                copy_col, view_col = st.columns([3, 1])
                                with copy_col:
                                    st.code(meta["sources"], language="json")
                                with view_col:
                                    if st.button("📋 Copy", key=f"copy_{i}"):
                                        st.toast("Copied to clipboard!", icon="✅")
                                        st.code(meta["sources"])  # This would need pyperclip for actual copy
                        st.markdown("---")
        
        st.markdown("<br>", unsafe_allow_html=True)

st.markdown("---")

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
            
            if "__interrupt__" in result:
                status.update(label="⚠️ Human intervention required", state="error")
                
                # Special handling for refund requests
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "⚠️ **Refund Request Detected**\n\nA refund has been requested and requires approval.",
                    "meta": {"intent": "refund", "decision": "Awaiting approval"},
                })
                
                # Enhanced approval UI
                st.markdown("---")
                st.warning("**🔔 Human-in-the-Loop Intervention Required**")
                
                approval_col1, approval_col2 = st.columns([2, 1])
                
                with approval_col1:
                    st.info("""
                    **Request Details:**
                    - Type: Refund Request
                    - Status: Pending Approval
                    - Thread ID: `{}`
                    - Requires manual review
                    """.format(st.session_state.thread_id))
                
                with approval_col2:
                    st.markdown("<br>" * 2, unsafe_allow_html=True)
                    if st.button("✅ **Approve Refund**", type="primary", use_container_width=True):
                        approve_payload = {
                            "thread_id": st.session_state.thread_id,
                            "approved": True,
                        }
                        
                        with st.spinner("Processing approval..."):
                            resumed = requests.post(
                                f"{API_URL}/resume",
                                json=approve_payload,
                                timeout=60,
                            ).json()
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"✅ **Approved:** {resumed.get('response')}",
                            "meta": {"intent": "refund", "decision": "Approved"},
                        })
                        st.rerun()
                    
                    if st.button("❌ **Deny Refund**", type="secondary", use_container_width=True):
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "❌ Refund request has been denied.",
                            "meta": {"intent": "refund", "decision": "Denied"},
                        })
                        st.rerun()
            
            else:
                intent_info = normalize_intent(result.get("intent"))

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result.get("result") or result.get("response"),
                    "meta": {
                        "intent": intent_info,        # 👈 KEEP OBJECT
                        "decision": result.get("decision"),
                        "sources": result.get("sources"),
                    },
                })


                status.update(label="✅ Response generated!", state="complete")
                st.success("Response added to conversation!")
        
        except requests.exceptions.RequestException as e:
            status.update(label="❌ Connection failed", state="error")
            st.error(f"API connection error: {str(e)}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"⚠️ **Connection Error:** Unable to reach the backend server. Please check if the API is running at {API_URL}",
                "meta": {"error": str(e)},
            })
        
        except Exception as e:
            status.update(label="❌ Unexpected error", state="error")
            st.error(f"Unexpected error: {str(e)}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"⚠️ **System Error:** {str(e)}",
                "meta": {"error": str(e)},
            })
    
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

