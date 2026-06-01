import os
import sys
sys.path.append('/c/ClaudeCodeShay/content_organizer')

# Set a dummy API key for testing
os.environ["NVIDIA_API_KEY"] = "dummy_key_for_testing"

from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock
import json

def test_process_url_endpoint():
    """Test the process-url endpoint with mocked LLM response."""

    # Mock the OpenAI client response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "content_type": "Recipe",
        "ingredients": ["2 cups flour", "1 cup sugar", "2 eggs"],
        "steps": ["Mix dry ingredients", "Add wet ingredients", "Bake at 350°F"],
        "name": None,
        "address": None,
        "google_maps_link": None
    })

    # Mock yt-dlp extraction
    mock_yt_dlp_info = {
        "title": "Test Recipe Video",
        "description": "This is a test recipe for chocolate chip cookies",
        "thumbnail": "https://example.com/thumbnail.jpg"
    }

    with patch('app.main.OpenAI') as mock_openai_class, \
         patch('yt_dlp.YoutubeDL') as mock_yt_dlp:

        # Setup OpenAI mock
        mock_openai_instance = MagicMock()
        mock_openai_class.return_value = mock_openai_instance
        mock_openai_instance.chat.completions.create.return_value = mock_response

        # Setup yt-dlp mock
        mock_yt_dlp_instance = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_yt_dlp_instance
        mock_yt_dlp_instance.extract_info.return_value = mock_yt_dlp_info

        # Create test client
        client = TestClient(app)

        # Make request
        response = client.post(
            "/process-url/",
            json={"url": "https://www.tiktok.com/@test/video/123"}
        )

        # Check response
        assert response.status_code == 200
        data = response.json()

        # Verify basic metadata
        assert data["title"] == "Test Recipe Video"
        assert data["description"] == "This is a test recipe for chocolate chip cookies"
        assert data["thumbnail_url"] == "https://example.com/thumbnail.jpg"

        # Verify LLM classification results
        assert data["content_type"] == "Recipe"
        assert data["ingredients"] == ["2 cups flour", "1 cup sugar", "2 eggs"]
        assert data["steps"] == ["Mix dry ingredients", "Add wet ingredients", "Bake at 350°F"]
        assert data["name"] is None
        assert data["address"] is None
        assert data["google_maps_link"] is None

        print("Endpoint test passed!")

if __name__ == "__main__":
    test_process_url_endpoint()