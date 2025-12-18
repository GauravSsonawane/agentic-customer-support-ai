import streamlit as st
import sys
from pathlib import Path

# Add project root to PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.agent_graph import build_graph


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from app.agent_graph import build_graph

st.set_page_config(page_title="Agentic Customer Support AI", layout="centered")

st.title("🤖 Agentic Customer Support AI")
st.caption("LangGraph • RAG • Human-in-the-Loop • Persistent State")

graph = build_graph()

# session-scoped thread_id
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "ui-thread-001"

query = st.text_input("Ask a question:")

if st.button("Submit") and query:
    state = {
        "query": query,
        "intent": None,
        "response": None,
        "escalate": False,
        "thread_id": st.session_state.thread_id,
    }

    try:
        result = graph.invoke(
            state,
            config={"configurable": {"thread_id": st.session_state.thread_id}},
        )

        if "__interrupt__" in result:
            st.warning("⚠ Human approval required")
            st.info(result["__interrupt__"][0].value)

            if st.button("Approve Refund"):
                interrupt_id = result["__interrupt__"][0].id
                resumed = graph.resume(
                    interrupt_id,
                    True,
                    config={"configurable": {"thread_id": st.session_state.thread_id}},
                )
                st.success(resumed["response"])
        else:
            st.success(result["response"])

    except Exception as e:
        st.error(str(e))
