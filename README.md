# Content Organizer API

A FastAPI backend for organizing TikTok/Instagram content. The app accepts video URLs, extracts metadata using yt-dlp, classifies content using an LLM (via Nvidia NIM), and saves structured data to SQLite.

## Features

- Accepts TikTok/Instagram URLs via POST request
- Uses yt-dlp to extract video metadata (title, description, thumbnail)
- Uses LLM (meta/llama-3.1-70b-instruct via Nvidia NIM) to classify content as:
  - Recipe
  - Restaurant
  - Place
- Extracts structured data based on classification:
  - Recipe: Ingredients list, Steps list
  - Restaurant/Place: Name, Address, Google Maps search link
- Saves all data to SQLite database
- Retrieve all stored content via GET request
- Automatic environment variable loading from .env file

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. The .env file is already configured with your NVIDIA_API_KEY
   (Normally you would create a .env file with: `NVIDIA_API_KEY="your_nvidia_api_key_here"`)
4. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

### Process URL
```
POST /process-url/
```

**Request Body:**
```json
{
  "url": "https://www.tiktok.com/@username/video/1234567890"
}
```

**Response:**
```json
{
  "id": 1,
  "url": "https://www.tiktok.com/@username/video/1234567890",
  "title": "Video Title",
  "description": "Video description",
  "thumbnail_url": "https://example.com/thumbnail.jpg",
  "content_type": "Recipe",
  "ingredients": ["ingredient1", "ingredient2"],
  "steps": ["step1", "step2"],
  "name": null,
  "address": null,
  "google_maps_link": null
}
```

### Get All Contents
```
GET /contents/
```

Returns a list of all stored content items.

### Health Check
```
GET /
```

Returns `{"message": "Content Organizer API"}`

## Database

The application uses SQLite with SQLAlchemy ORM. The database file is created automatically as `content_organizer.db` in the project root.

## Environment Variables

- `NVIDIA_API_KEY`: Loaded automatically from .env file for accessing Nvidia NIM's LLM API

## Dependencies

See `requirements.txt` for full list:
- fastapi
- uvicorn
- pydantic
- yt-dlp
- sqlalchemy
- openai
- python-dotenv

## Notes

- The LLM classification is designed to handle Hebrew content
- All extracted data is stored as JSON strings in the database for flexibility
- Error handling is included for yt-dlp extraction and LLM API calls
- Environment variables are automatically loaded from .env file using python-dotenv