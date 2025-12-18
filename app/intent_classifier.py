from app.llm_intent_classifier import classify_intent_llm

def classify_intent(query: str):
    return classify_intent_llm(query)

