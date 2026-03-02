import os
import pytest
from unittest.mock import patch, MagicMock

# Set dummy environment variables before importing any app code
os.environ["SUPABASE_URL"] = "http://localhost:8000"
os.environ["SUPABASE_KEY"] = "dummy_key"
os.environ["GEMINI_API_KEY"] = "dummy_gemini_key"

@pytest.fixture(autouse=True)
def mock_supabase_and_gemini():
    """
    Mock external dependencies for all tests so we don't hit real APIs during CI
    or fail if local .env isn't populated aggressively enough.
    """
    with patch("dependencies.supabase") as mock_supa, \
         patch("ai.multimodal.client") as mock_gemini:
        
        # Setup basic mock return values if needed by specific tests
        mock_supa.auth.get_user.return_value = MagicMock(user=MagicMock(id="mock_user_123", email="test@test.com"))
        
        yield mock_supa, mock_gemini
