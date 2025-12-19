"""app.api package: exposes API route modules.

Creating this file makes `app.api` a proper Python package so imports
like `from app.api.routes import router` succeed when running Uvicorn.
"""

__all__ = ["routes"]
