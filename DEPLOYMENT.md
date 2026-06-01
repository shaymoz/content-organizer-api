# Deploying Content Organizer API to Render

This guide explains how to deploy the Content Organizer FastAPI application to Render.

## 📋 Prerequisites

1. A Render account (https://render.com)
2. GitHub repository with the code (you can push this folder to a new repo)
3. The `.env` file is already configured with your NVIDIA_API_KEY (do not commit this to public repos!)

## 🔧 Preparation Steps

### 1. Update .gitignore (if not already present)
Make sure your `.gitignore` includes:
```
# Environment variables
.env
# Python
__pycache__/
*.py[cod]
*$py.class
# SQLite
*.db
# Virtual environments
venv/
ENV/
env/
```

### 2. Prepare for Render Deployment
The project is already configured for Render with:
- **Procfile**: Contains the gunicorn command for production
- **render.yaml**: Optional Render service definition
- **Updated main.py**: Binds to 0.0.0.0 and uses PORT environment variable
- **requirements.txt**: Includes gunicorn for production

### 3. Important Security Note
The `.env` file contains your NVIDIA_API_KEY. For security:
- **Do not commit `.env` to public GitHub repositories**
- On Render, you'll add this as an environment variable instead
- For local development, the .env file works fine

## 🚀 Deployment Options

### Option 1: Manual Deployment via Render Dashboard

1. **Push code to GitHub** (excluding .env file):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/content-organizer.git
   git push -u origin main
   ```

2. **On Render Dashboard**:
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: content-organizer
     - **Region**: Choose your preferred region
     - **Branch**: main
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
   - Click "Advanced" → "Environment"
   - Add Environment Variable:
     - **Key**: NVIDIA_API_KEY
     - **Value**: [Your actual API key from .env file]
     - **Check**: "This is a sensitive value"
   - Click "Create Web Service"

### Option 2: Using render.yaml (Alternative)

1. **Update render.yaml** with your actual values (if needed)
2. **Push to GitHub**
3. **On Render**:
   - Click "New" → "Blueprints"
   - Connect your repository
   - Render will auto-detect the render.yaml file
   - Add the NVIDIA_API_KEY environment variable when prompted

## 🔍 Environment Variables on Render

In the Render dashboard, under your service's "Environment" section, add:

| Key | Value | Notes |
|-----|-------|-------|
| NVIDIA_API_KEY | [Your actual key] | From your .env file - mark as sensitive |

No other environment variables are required - the app will:
- Bind to 0.0.0.0 (hardcoded in start command)
- Use PORT from Render's environment (automatically provided)
- Load other settings from code defaults

## 🧪 Testing After Deployment

Once deployed, test your endpoints:

1. **Health Check**:
   ```
   GET https://your-service.onrender.com/
   ```
   Should return: `{"message": "Content Organizer API"}`

2. **Process URL**:
   ```
   POST https://your-service.onrender.com/process-url/
   Body: {"url": "https://www.tiktok.com/@example/video/123"}
   ```

3. **Get All Content**:
   ```
   GET https://your-service.onrender.com/contents/
   ```

## 📝 Notes

- The application uses SQLite which persists data on Render's persistent disk
- Gunicorn with Uvicorn workers is used for production performance
- The app automatically handles Hebrew content in video descriptions via the LLM prompt
- All extracted data is saved alongside basic metadata in the SQLite database
- Environment variables are loaded automatically - no additional configuration needed

## 🔄 Updating Your Deployment

When you make changes to your code:
1. Commit and push to GitHub
2. Render will automatically detect changes and redeploy (if auto-deploy is enabled)
3. Or manually trigger a deploy from the Render dashboard

## ⚠️ Troubleshooting

If you encounter issues:
1. Check the Render deployment logs
2. Verify the NVIDIA_API_KEY is correctly set in environment variables
3. Ensure the start command matches what's in your Procfile
4. Check that requirements.txt includes all necessary packages

## ✅ Summary

Your Content Organizer API is now ready for deployment to Render with:
- Automatic binding to 0.0.0.0 and dynamic PORT usage
- Production-ready gunicorn configuration
- Secure environment variable handling
- Full LLM integration for content classification
- Hebrew content handling capability
- Automatic environment loading (for local development)

**Happy deploying!** 🚀