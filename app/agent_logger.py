import logging

logger = logging.getLogger(__name__)


def log_step(node_name: str, state: dict):
    logger.info(f"NODE: {node_name}")
    logger.debug(f"STATE: {state}")
