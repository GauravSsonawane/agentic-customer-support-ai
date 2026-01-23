import streamlit as st
from ui.components.utils import get_intent_color

def render_chat_history():
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
                            
                            intent_label = None
                            if isinstance(meta.get("intent"), dict):
                                intent_label = meta["intent"].get("label")
                            elif isinstance(meta.get("intent"), str):
                                intent_label = meta["intent"]

                            # 🔒 SAFETY CHECK
                            if intent_label:
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
                                    if meta.get("confidence") is not None:
                                        st.metric("Confidence Score", meta["confidence"])
                                
                                with col_b:
                                    if meta.get("reason"):
                                        st.info(f"**Reason:** {meta['reason']}")
                            
                            # Decision
                            if meta.get("decision"):
                                st.success(f"**Decision Made:** {meta['decision']}")
                            
                            # Sources with copy button
                            sources = meta.get("sources")

                            if isinstance(sources, str) and sources.strip():
                                st.markdown("**📚 Sources Used:**")

                                # Add copy button
                                copy_col, view_col = st.columns([3, 1])
                                with copy_col:
                                    st.code(sources)
                                with view_col:
                                    if st.button("📋 Copy", key=f"copy_{i}"):
                                        st.toast("Copied to clipboard!", icon="✅")

                            st.markdown("---")

            st.markdown("<br>", unsafe_allow_html=True) 
            
    st.markdown("---")
