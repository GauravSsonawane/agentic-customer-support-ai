import streamlit as st
import time
from ui.components.utils import get_intent_color

def render_sidebar():
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
        
def render_metrics(api_url):
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
            st.metric("API Status", "Connected" if api_url else "Disconnected")
            st.caption("Backend connection")
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
