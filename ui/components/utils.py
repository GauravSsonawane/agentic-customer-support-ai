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


CUSTOM_CSS = """
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
"""
