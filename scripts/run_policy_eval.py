import requests
import csv
import time

API_URL = "http://localhost:8000/query"

QUESTIONS = [
    "Can I return a product if it arrives damaged?",
    "What is your return policy for damaged items?",
    "Can I return a product with missing accessories?",
    "What if the product I received is different from its description?",
    "Are defective products eligible for return?",
    "Can international orders be returned?",
    "Can I get a refund for a damaged item?",
    "I want a refund for my order",
    "Please process my refund",
    "Can I return it?",
]

results = []

for q in QUESTIONS:
    payload = {
        "query": q,
        "thread_id": "eval-thread"
    }

    r = requests.post(API_URL, json=payload)
    data = r.json()

    results.append({
        "question": q,
        "answer": data.get("final_answer"),
        "decision": data.get("decision"),
        "escalate": data.get("escalate"),
        "confidence": data.get("confidence"),
    })

    time.sleep(0.5)  # be nice to your local LLM 😄

# Save results
with open("policy_eval_results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["question", "answer", "decision", "escalate", "confidence"]
    )
    writer.writeheader()
    writer.writerows(results)

print("✅ Evaluation complete. Results saved to policy_eval_results.csv")
