import json
from datetime import datetime
from pathlib import Path

TRACE_DIR = Path("traces")
TRACE_DIR.mkdir(exist_ok=True)


def trace_event(event_type: str, data: dict, thread_id: str):
    trace = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,
        "data": data,
    }

    trace_file = TRACE_DIR / f"{thread_id}.jsonl"
    with open(trace_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(trace) + "\n")
