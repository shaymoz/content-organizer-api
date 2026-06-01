import os
import sys
sys.path.append('/c/ClaudeCodeShay/content_organizer')

# Test that tiktok-scraper integration is properly structured
def test_tiktok_scraper_integration():
    """Test that the tiktok-scraper integration is properly structured."""
    # Check that we can import the main components
    from app.main import app, TIKTOK_SCRAPER_AVAILABLE

    # Check that the scraper availability flag is a boolean
    assert isinstance(TIKTOK_SCRAPER_AVAILABLE, bool)

    # Check that the app is a FastAPI instance
    from fastapi import FastAPI
    assert isinstance(app, FastAPI)

    print("TikTok scraper integration structure test passed!")
    print(f"TikTok scraper available: {TIKTOK_SCRAPER_AVAILABLE}")

if __name__ == "__main__":
    test_tiktok_scraper_integration()