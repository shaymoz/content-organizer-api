# Content Organizer API - Startup Instructions

## 🚀 Quick Start

The application is ready to run with **zero manual environment setup** thanks to the pre-configured .env file.

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Server
```bash
uvicorn app.main:app --reload
```

### 3. Test the API
- **Process a URL**: POST to `http://localhost:8000/process-url/` with JSON body: `{"url": "https://www.tiktok.com/@example/video/123"}`
- **View All Content**: GET from `http://localhost:8000/contents/`
- **Health Check**: GET from `http://localhost:8000/`

## 🔧 Configuration

### Environment Variables
The `NVIDIA_API_KEY` is already configured in the `.env` file:
```
NVIDIA_API_KEY=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
```

This is automatically loaded on startup via `python-dotenv` - no manual export needed!

### Database
- SQLite database automatically created as `content_organizer.db`
- Tables created on first run via SQLAlchemy

## 📁 Project Structure
```
content_organizer/
├── .env                    # Environment variables (PRE-CONFIGURED)
├── requirements.txt        # Python dependencies
├── README.md              # Documentation
├── STATUS.md              # Implementation status
├── STARTUP.md             # This file
├── app/
│   ├── __init__.py
│   ├── database.py        # SQLite connection
│   ├── models.py         # Pydantic & SQLAlchemy models
│   └── main.py           # FastAPI app with LLM integration
└── content_organizer.db   # SQLite database (auto-created)
```

## 🎯 Features
- ✅ Accepts TikTok/Instagram URLs via POST request
- ✅ Uses yt-dlp to extract video metadata (title, description, thumbnail)
- ✅ Uses LLM (meta/llama-3.1-70b-instruct via Nvidia NIM) to classify content
- ✅ Handles Hebrew content appropriately in descriptions
- ✅ For Recipe: extracts ingredients and steps as JSON lists
- ✅ For Restaurant/Place: extracts name, address, and generates Google Maps search URL
- ✅ Saves all data to SQLite database alongside basic metadata
- ✅ Automatic environment variable loading from .env file
- ✅ Comprehensive error handling with fallback responses

## 🛠️ Development
To modify the NVIDIA_API_KEY:
1. Edit the `.env` file
2. Restart the server

To update dependencies:
```bash
pip install -r requirements.txt
```

## 📝 Notes
- The LLM prompt is specifically designed to handle Hebrew text in video descriptions
- All extracted data is stored as JSON strings in the database for flexibility
- The application includes proper error handling for both yt-dlp and LLM API calls
- Environment variables are loaded automatically - no manual terminal setup required