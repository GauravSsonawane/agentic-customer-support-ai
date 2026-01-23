__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import logging
from fastapi import FastAPI
from app.api.routes import router
from app.observability import setup_observability

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(title="Agentic Customer Support AI")

# Setup Observability
setup_observability(app)

app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
