from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from . import models, database
import yt_dlp
import json
from typing import List, Optional
import os
import re
from dotenv import load_dotenv
from openai import OpenAI

# Import tiktok-scraper
try:
    from tiktok_scraper.scraper import scrape_video
    from tiktok_scraper.scraper import ScrapeUtils
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    TIKTOK_SCRAPER_AVAILABLE = True
except ImportError:
    TIKTOK_SCRAPER_AVAILABLE = False
    # No warning print to avoid cluttering logs in production

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Content Organizer API")

# Dependency to get database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize OpenAI client for Nvidia NIM
def get_openai_client():
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise ValueError("NVIDIA_API_KEY environment variable is not set")
    return OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key
    )

def classify_content_with_llm(description: str) -> dict:
    """
    Use LLM to classify content and extract structured data.
    Returns a dictionary with classification results.
    """
    client = get_openai_client()

    prompt = f"""
Analyze the following video description and classify the content into one of these categories: 'Recipe', 'Restaurant', or 'Place'.

Description:
{description}

Based on the classification, extract the relevant structured data:

If Recipe:
- Extract ingredients as a JSON list of strings
- Extract steps as a JSON list of strings

If Restaurant or Place:
- Extract the name as a string
- Extract the address as a string
- Generate a Google Maps search URL using the name and address

IMPORTANT: The description may be in Hebrew. Handle Hebrew text appropriately.

Return ONLY a valid JSON object with the following structure:
{{
    "content_type": "Recipe" | "Restaurant" | "Place",
    "ingredients": ["ingredient1", "ingredient2", ...] | null,
    "steps": ["step1", "step2", ...] | null,
    "name": "string" | null,
    "address": "string" | null,
    "google_maps_link": "string" | null
}}

For Recipe: ingredients and steps should be populated, name/address/google_maps_link should be null.
For Restaurant/Place: name, address, and google_maps_link should be populated, ingredients/steps should be null.
"""

    try:
        completion = client.chat.completions.create(
            model="meta/llama-3.1-70b-instruct",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            top_p=0.7,
            max_tokens=1024,
        )

        # Extract the JSON response
        result_text = completion.choices[0].message.content.strip()

        # Parse JSON response
        import json
        result = json.loads(result_text)

        # Validate required fields
        required_fields = ["content_type", "ingredients", "steps", "name", "address", "google_maps_link"]
        for field in required_fields:
            if field not in result:
                result[field] = None

        return result

    except Exception as e:
        print(f"Error calling LLM: {e}")
        # Return fallback classification
        return {
            "content_type": "Recipe",
            "ingredients": None,
            "steps": None,
            "name": None,
            "address": None,
            "google_maps_link": None
        }

# Create tables
models.Base.metadata.create_all(bind=database.engine)

@app.post("/process-url/", response_model=models.ContentResponse)
async def process_url(url_input: models.URLInput, db: Session = Depends(get_db)):
    """
    Accept a TikTok/Instagram URL, fetch video metadata using yt-dlp,
    extract thumbnail, classify content, and save to database.
    """
    # Extract video information using tiktok-scraper for TikTok URLs, otherwise yt-dlp with timeout and headers
    def extract_video_info(url):
        # Check if it's a TikTok URL and tiktok-scraper is available
        if 'tiktok.com' in url and TIKTOK_SCRAPER_AVAILABLE:
            try:
                # Setup Chrome options for headless browsing
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--window-size=1920,1080")

                # Initialize the driver
                driver = webdriver.Chrome(options=chrome_options)

                try:
                    # Scrape the TikTok video
                    scraped_data = scrape_video(driver, folder='./temp_tiktok')

                    # Close the driver
                    driver.quit()

                    # If scrape_video returns a list, take the first item
                    if isinstance(scraped_data, list) and len(scraped_data) > 0:
                        scraped_data = scraped_data[0]
                    elif isinstance(scraped_data, list):
                        # Empty list, return empty data
                        return {
                            'title': '',
                            'description': '',
                            'thumbnail': ''
                        }

                    # Map scraped data to the expected format (title, description, thumbnail)
                    # Based on tiktok-scraper output structure
                    title = scraped_data.get('title', '') or scraped_data.get('desc', '')
                    description = scraped_data.get('desc', '')
                    # Thumbnail is typically in the 'cover' field
                    thumbnail = scraped_data.get('cover', '') or scraped_data.get('thumbnail', '')

                    # Clean up temp files if they exist
                    import os
                    import shutil
                    if os.path.exists('./temp_tiktok'):
                        shutil.rmtree('./temp_tiktok')

                    return {
                        'title': title,
                        'description': description,
                        'thumbnail': thumbnail
                    }
                except Exception as e:
                    # Make sure to close driver on error
                    try:
                        driver.quit()
                    except:
                        pass
                    raise e  # Re-raise to be caught by outer exception handler

            except Exception as e:
                # If tiktok-scraper fails, fall back to yt-dlp
                print(f"tiktok-scraper failed: {e}. Falling back to yt-dlp.")
                pass  # Fall through to yt-dlp below

        # For non-TikTok URLs or when tiktok-scraper fails, use yt-dlp
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 15,  # 15 seconds timeout
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
            }
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            # yt-dlp returns a dict with at least title, description, thumbnail
            return {
                'title': info.get('title', ''),
                'description': info.get('description', ''),
                'thumbnail': info.get('thumbnail', '')
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error extracting video info: {str(e)}")

    # Use the extract_video_info function
    info = extract_video_info(url_input.url)
    title = info.get('title', '')
    description = info.get('description', '')
    thumbnail_url = info.get('thumbnail', '')

    # Implement LLM-based classification and structured data extraction
    # Use the description (which may contain transcript/summary) for classification
    classification_result = classify_content_with_llm(description)

    content_type = classification_result.get("content_type", "Recipe")
    ingredients = classification_result.get("ingredients")
    steps = classification_result.get("steps")
    name = classification_result.get("name")
    address = classification_result.get("address")
    google_maps_link = classification_result.get("google_maps_link")

    # Create database entry
    db_content = models.Content(
        url=url_input.url,
        title=title,
        description=description,
        thumbnail_url=thumbnail_url,
        content_type=content_type,
        ingredients=json.dumps(ingredients) if ingredients else None,
        steps=json.dumps(steps) if steps else None,
        name=name,
        address=address,
        google_maps_link=google_maps_link
    )

    db.add(db_content)
    db.commit()
    db.refresh(db_content)

    # Prepare response
    response = models.ContentResponse(
        id=db_content.id,
        url=db_content.url,
        title=db_content.title,
        description=db_content.description,
        thumbnail_url=db_content.thumbnail_url,
        content_type=db_content.content_type,
        ingredients=json.loads(db_content.ingredients) if db_content.ingredients else None,
        steps=json.loads(db_content.steps) if db_content.steps else None,
        name=db_content.name,
        address=db_content.address,
        google_maps_link=db_content.google_maps_link
    )

    return response

@app.get("/contents/", response_model=list[models.ContentResponse])
async def get_contents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all content entries from the database.
    """
    contents = db.query(models.Content).offset(skip).limit(limit).all()
    # Convert JSON strings back to lists
    result = []
    for content in contents:
        result.append(models.ContentResponse(
            id=content.id,
            url=content.url,
            title=content.title,
            description=content.description,
            thumbnail_url=content.thumbnail_url,
            content_type=content.content_type,
            ingredients=json.loads(content.ingredients) if content.ingredients else None,
            steps=json.loads(content.steps) if content.steps else None,
            name=content.name,
            address=content.address,
            google_maps_link=content.google_maps_link
        ))
    return result

@app.get("/")
async def root():
    return {"message": "Content Organizer API"}


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host=host, port=port, reload=False)