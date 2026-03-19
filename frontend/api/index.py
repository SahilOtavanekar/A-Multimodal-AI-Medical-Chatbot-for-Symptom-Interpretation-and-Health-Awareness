import os
import sys

# Path to the 'backend' folder relative to this file (api/index.py)
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Add the backend folder to the path so imports (main, routers, etc.) work
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import the FastAPI app from backend/main.py
try:
    from main import app as fastapi_app
    # Vercel's Python runtime searches for a variable named 'app' by default
    app = fastapi_app
except ImportError as e:
    print(f"CRITICAL ERROR importing backend: {e}")
    # We create a dummy app to respond with the error if import fails
    from fastapi import FastAPI
    app = FastAPI()
    @app.get("/api/(.*)")
    def error():
        return {"success": False, "error": f"Import failed: {e}"}
