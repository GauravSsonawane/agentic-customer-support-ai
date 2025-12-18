import streamlit as st
import sys
from pathlib import Path
import requests

# -------------------------------
# Setup PYTHONPATH
# -------------------------------
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

# -------------------------------
# Backend API URL (Async boundary)
# -------------------------------
API_URL = "http://localhost:8000/query"


def normalize_intent(intent):
    """
    Normalizes intent to a UI-safe dict
    """
    if intent is None:
        return None

    # LLM intent object
    if hasattr(intent, "intent"):
        return {
            "label": intent.intent.value,
            "confidence": intent.confidence,
            "reason": intent.reason,
        }

    # Enum intent
    if hasattr(intent, "value"):
        return {
            "label": intent.value,
            "confidence": "N/A",
            "reason": "Rule-based routing",
        }

    # String intent
    if isinstance(intent, str):
        return {
            "label": intent,
            "confidence": "N/A",
            "reason": "Backend fallback",
        }

    return None


# -------------------------------
# Streamlit Page Config
# -------------------------------
st.set_page_config(
    page_title="Agentic Customer Support AI",
    layout="centered",
)

st.title("🤖 Agentic Customer Support AI")
st.caption("LangGraph • RAG • Human-in-the-Loop • Persistent State")

# -------------------------------
# Session state
# -------------------------------
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "ui-thread-001"

if "response" not in st.session_state:
    st.session_state.response = None

# -------------------------------
# User input
# -------------------------------
query = st.text_input("Ask a question:")

if st.button("Submit") and query:
    payload = {
        "query": query,
        "thread_id": st.session_state.thread_id,
    }

    try:
        with st.spinner("Thinking..."):
            resp = requests.post(
                API_URL,
                json=payload,
                timeout=60,
            )

        if resp.status_code != 200:
            st.error("Backend error")
            st.stop()

        result = resp.json()

        # ---------------------------
        # Human-in-the-loop
        # ---------------------------
        if "__interrupt__" in result:
            st.warning("⚠ Human approval required")
            st.info(result["__interrupt__"][0]["value"])

            if st.button("Approve Refund"):
                approve_payload = {
                    "thread_id": st.session_state.thread_id,
                    "approved": True,
                }

                resumed = requests.post(
                    f"{API_URL}/resume",
                    json=approve_payload,
                    timeout=60,
                ).json()

                st.session_state.response = resumed
        else:
            st.session_state.response = result

    except requests.exceptions.RequestException as e:
        st.error(f"API error: {e}")

# -------------------------------
# Render assistant response
# -------------------------------
if st.session_state.response:
    response = st.session_state.response

    st.markdown("### 🤖 Assistant")
    st.write(response.get("result") or response.get("response"))

    # ---------------------------
    # Explainability Panel
    # ---------------------------
    with st.expander("🔍 Why this answer?"):
        with st.expander("🔍 Why this answer?"):
            intent_info = normalize_intent(response.get("intent"))

            if intent_info:
                st.markdown(f"**Intent:** `{intent_info['label']}`")
                st.markdown(f"**Confidence:** `{intent_info['confidence']}`")
                st.markdown(f"**Reason:** {intent_info['reason']}")

            if "decision" in response:
                st.markdown(f"**Decision:** `{response['decision']}`")

            if "sources" in response and response["sources"]:
                st.markdown("**Sources used:**")
                st.code(response["sources"])

