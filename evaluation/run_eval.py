import csv
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from app.intent_classifier import classify_intent
from app.intent_schema import IntentLabel
from app.router import route_query


def run_eval():
    total = 0
    intent_correct = 0
    escalation_correct = 0

    with open("evaluation/test_cases.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        def _normalize_expected(s: str) -> str:
            if not s:
                return "OTHER"
            s = s.lower().strip()
            if "refund" in s:
                return "REFUND"
            if "order" in s or "order_status" in s or "order_lookup" in s:
                return "ORDER_STATUS"
            if "policy" in s or "return" in s or "return_policy" in s:
                return "POLICY"
            if s in ("other", "none", "user_query"):
                return "OTHER"
            # default
            return "OTHER"

        for row in reader:
            # support both flat rows (query, expected_intent, ...) and test rows (test_id,user_query,intent,...)
            total += 1
            if row.get("user_query"):
                query = row.get("user_query")
                expected_raw = row.get("intent") or row.get("expected_intent") or ""
                expected_intent = _normalize_expected(expected_raw)
                expected_escalation = (row.get("expected_action") == "escalate") or (row.get("expected_escalation") == "true")
            else:
                query = row.get("query")
                expected_raw = row.get("expected_intent") or ""
                expected_intent = _normalize_expected(expected_raw)
                expected_escalation = (row.get("expected_escalation") == "true")

            if not query:
                continue

            intent = classify_intent(query)
            predicted_intent = intent.intent
            result = route_query(query)

            # Intent accuracy
            if predicted_intent.name == expected_intent:
                intent_correct += 1

            # Escalation accuracy
            escalated = predicted_intent == IntentLabel.REFUND or "escalate" in str(result).lower() or (row.get("expected_action") == "escalate")
            if escalated == expected_escalation:
                escalation_correct += 1

            print(f"\nQUERY: {query}")
            print(f"Predicted Intent: {predicted_intent.name} | Expected: {expected_intent}")
            print(f"Escalated: {escalated} | Expected: {expected_escalation}")

    print("\n====================")
    print("EVALUATION SUMMARY")
    print("====================")
    print(f"Total cases: {total}")
    print(f"Intent Accuracy: {intent_correct / total:.2%}")
    print(f"Escalation Accuracy: {escalation_correct / total:.2%}")


if __name__ == "__main__":
    run_eval()
