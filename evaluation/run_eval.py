import csv
import requests
import time

API_URL = "http://127.0.0.1:8000/query"
THREAD_ID = "eval-thread"

input_file = "evaluation/questions.csv"
output_file = "evaluation/results.csv"

results = []

with open(input_file, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        query = row["query"]

        payload = {
            "query": query,
            "thread_id": THREAD_ID
        }

        print(f"➡️ Testing: {query}")

        resp = requests.post(API_URL, json=payload)

        if resp.status_code != 200:
            results.append({
                "id": row["id"],
                "query": query,
                "error": resp.text
            })
            continue

        data = resp.json()

        results.append({
            "id": row["id"],
            "query": query,
            "final_answer": data.get("final_answer"),
            "decision": data.get("decision"),
            "intent": str(data.get("intent")),
            "confidence": data.get("confidence"),
            "escalate": data.get("escalate")
        })

        time.sleep(0.5)  # avoid rate issues

# Save results
with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=results[0].keys()
    )
    writer.writeheader()
    writer.writerows(results)

print("✅ Evaluation completed. Results saved to evaluation/results.csv")

