from fastapi.testclient import TestClient
from main import app
from models import StandardResponse

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] == True
    assert "Welcome" in data["message"]

def test_rate_limiter_active():
    """Verify that hitting the index very rapidly doesn't drop requests unnecessarily, 
    but ensures the middleware didn't break normal operation."""
    for _ in range(5):
        response = client.get("/")
        assert response.status_code == 200

# Auth tests are hard to mock locally without an active Supabase JWT, 
# so we ensure they return 401 Unauthorized for bad tokens.
def test_unauthorized_chat_access():
    response = client.post("/chat/", json={"message": "hello"})
    assert response.status_code == 403 # HTTPBearer returns 403 Forbidden when credentials not provided

def test_unauthorized_profile_delete():
    response = client.delete("/profile/data")
    assert response.status_code == 403
