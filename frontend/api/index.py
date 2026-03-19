import os
import sys

# Path to the 'backend' folder relative to this file (frontend/api/index.py)
# We go up two levels to reach the repo root: api/ -> frontend/ -> root/
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

# Add the backend folder to the path so imports (main, routers, etc.) work
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import the FastAPI app from backend/main.py
try:
    from main import app
    handler = app
except ImportError as e:
    print(f"Error importing backend: {e}")
    raise e
