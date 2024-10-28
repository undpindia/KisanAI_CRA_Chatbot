"""
asgi.py
-------

ASGI entry point for running the FastAPI application.

This file can be used to run the FastAPI app locally or to deploy the app to an ASGI server like Uvicorn.
"""

# from app.src.main import app
from app.src.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.src.main:app", host="0.0.0.0", port=8000, reload=True)