from pathlib import Path

# Prefer SqliteSaver if available, otherwise fall back to an in-memory saver.
# The sqlite saver may be provided by an extra package such as
# `langgraph-checkpoint-sqlite` or similar. To persist checkpoints across runs,
# install the appropriate provider and restore the SqliteSaver import.

CHECKPOINT_DIR = Path("checkpoints")
CHECKPOINT_DIR.mkdir(exist_ok=True)

CHECKPOINT_DB = CHECKPOINT_DIR / "agent_state.db"

try:
	from langgraph.checkpoint.sqlite import SqliteSaver

	checkpointer = SqliteSaver.from_path(str(CHECKPOINT_DB))
except Exception:
	from langgraph.checkpoint.memory import InMemorySaver

	# InMemorySaver does not persist across process restarts.
	checkpointer = InMemorySaver()
