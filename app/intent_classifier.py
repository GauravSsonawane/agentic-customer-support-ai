from app.llm import get_llm
from app.intent import Intent


def classify_intent(query: str) -> Intent:
    """
    Classify user intent into a small fixed set.
    """

    prompt = f"""
Classify the user query into ONE of the following categories:
- refund
- policy
- order_status
- other

Respond with ONLY the category name.

Query:
{query}
"""

    llm = get_llm()
    response = llm.invoke(prompt).content.strip().lower()
    
    if response == "refund":
            return Intent.REFUND
    elif response == "policy":
        return Intent.POLICY
    elif response == "order_status":
        return Intent.ORDER_STATUS
    else:
        return Intent.OTHER
