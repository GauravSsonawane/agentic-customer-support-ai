import csv
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from app.intent_classifier import classify_intent
from app.intent import Intent
from app.router import route_query


def run_eval():
    total = 0
    intent_correct = 0
    escalation_correct = 0

    with open("evaluation/test_cases.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            total += 1
            query = row["query"]
            expected_intent = row["expected_intent"]
            expected_escalation = row["expected_escalation"] == "true"

            intent = classify_intent(query)
            result = route_query(query)

            # Intent accuracy
            if intent.name == expected_intent:
                intent_correct += 1

            # Escalation accuracy
            escalated = intent in [Intent.REFUND] or "escalated" in str(result).lower()
            if escalated == expected_escalation:
                escalation_correct += 1

            print(f"\nQUERY: {query}")
            print(f"Predicted Intent: {intent.name} | Expected: {expected_intent}")
            print(f"Escalated: {escalated} | Expected: {expected_escalation}")

    print("\n====================")
    print("EVALUATION SUMMARY")
    print("====================")
    print(f"Total cases: {total}")
    print(f"Intent Accuracy: {intent_correct / total:.2%}")
    print(f"Escalation Accuracy: {escalation_correct / total:.2%}")


if __name__ == "__main__":
    run_eval()
