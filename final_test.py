import os
import sys
sys.path.append('/c/ClaudeCodeShay/content_organizer')

# Set a dummy API key for testing
os.environ["NVIDIA_API_KEY"] = "dummy_key_for_testing"

from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock
import json

def test_recipe_classification():
    """Test the endpoint with a recipe classification."""

    # Mock the OpenAI client response for a recipe
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "content_type": "Recipe",
        "ingredients": ["2 cups flour", "1 cup sugar", "2 eggs", "1/2 cup butter"],
        "steps": ["Preheat oven to 350°F", "Mix dry ingredients", "Add wet ingredients", "Bake for 25 minutes"],
        "name": None,
        "address": None,
        "google_maps_link": None
    })

    # Mock yt-dlp extraction
    mock_yt_dlp_info = {
        "title": "Chocolate Chip Cookie Recipe",
        "description": "Learn how to make delicious chocolate chip cookies from scratch",
        "thumbnail": "https://example.com/cookie-thumbnail.jpg"
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
            json={"url": "https://www.tiktok.com/@cooking/video/123"}
        )

        # Check response
        assert response.status_code == 200
        data = response.json()

        # Verify basic metadata
        assert data["title"] == "Chocolate Chip Cookie Recipe"
        assert data["description"] == "Learn how to make delicious chocolate chip cookies from scratch"
        assert data["thumbnail_url"] == "https://example.com/cookie-thumbnail.jpg"

        # Verify LLM classification results for recipe
        assert data["content_type"] == "Recipe"
        assert data["ingredients"] == ["2 cups flour", "1 cup sugar", "2 eggs", "1/2 cup butter"]
        assert data["steps"] == ["Preheat oven to 350°F", "Mix dry ingredients", "Add wet ingredients", "Bake for 25 minutes"]
        assert data["name"] is None
        assert data["address"] is None
        assert data["google_maps_link"] is None

        print("Recipe classification test passed!")

def test_restaurant_classification():
    """Test the endpoint with a restaurant classification."""

    # Mock the OpenAI client response for a restaurant
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "content_type": "Restaurant",
        "ingredients": None,
        "steps": None,
        "name": "Mom's Falafel",
        "address": "123 Herzl St, Tel Aviv, Israel",
        "google_maps_link": "https://www.google.com/maps/search/?api=1&query=Mom's%20Falafel%20123%20Herzl%20St%20Tel%20Aviv%20Israel"
    })

    # Mock yt-dlp extraction
    mock_yt_dlp_info = {
        "title": "Best Falafel in Tel Aviv",
        "description": "Hidden gem falafel place in Tel Aviv serving the best falafel pita",
        "thumbnail": "https://example.com/falafel-thumbnail.jpg"
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
            json={"url": "https://www.instagram.com/p/ABC123/"}
        )

        # Check response
        assert response.status_code == 200
        data = response.json()

        # Verify basic metadata
        assert data["title"] == "Best Falafel in Tel Aviv"
        assert data["description"] == "Hidden gem falafel place in Tel Aviv serving the best falafel pita"
        assert data["thumbnail_url"] == "https://example.com/falafel-thumbnail.jpg"

        # Verify LLM classification results for restaurant
        assert data["content_type"] == "Restaurant"
        assert data["ingredients"] is None
        assert data["steps"] is None
        assert data["name"] == "Mom's Falafel"
        assert data["address"] == "123 Herzl St, Tel Aviv, Israel"
        assert "google.com/maps" in data["google_maps_link"]
        assert "Mom's%20Falafel" in data["google_maps_link"]

        print("Restaurant classification test passed!")

if __name__ == "__main__":
    test_recipe_classification()
    test_restaurant_classification()
    print("All tests passed!")