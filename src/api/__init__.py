# app/api/__init__.py
from .graph_api import app  # re-exporta para poder correr: uvicorn app.api:app
__all__ = ["app"]
