# Technology Stack & Build System

## Backend Stack
- **Framework**: Flask 2.3.3 (Python web framework)
- **Audio Processing**: yt-dlp (YouTube/SoundCloud downloader)
- **File Handling**: Built-in Python libraries (zipfile, shutil, os)
- **Server**: Gunicorn for production deployment

## Frontend Stack
- **CSS Framework**: Bootstrap 5.3.0
- **Icons**: Font Awesome 6.4.0
- **Fonts**: Google Fonts (Inter family)
- **JavaScript**: Vanilla ES6+ (no frameworks)
- **Design System**: Custom CSS with glassmorphism effects

## Key Dependencies
```
flask==2.3.3
requests==2.31.0
python-dotenv>=0.19.0
yt-dlp>=2023.12.30
gunicorn
```

## Development Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
# Runs on http://localhost:5000 with debug=True
```

### Production Deployment
```bash
# Using Gunicorn (configured in Procfile)
gunicorn app:app

# Or direct Flask production
python app.py
# Uses production config when not in debug mode
```

## File Structure Conventions
- **Downloads**: All files saved to `descargas/` directory
- **Templates**: Jinja2 templates in `templates/` folder
- **Static Assets**: CDN-hosted (Bootstrap, Font Awesome, Google Fonts)
- **Configuration**: Environment-based settings in app.py

## Audio Processing Pipeline
1. **URL Validation**: Check for valid SoundCloud URLs
2. **Content Detection**: Automatically detect single track vs playlist
3. **Download**: Use yt-dlp with FLAC preference, MP3 fallback
4. **Post-Processing**: Optional ZIP compression for playlists
5. **File Management**: Organize in downloads directory with metadata

## Deployment Configuration
- **Platform**: Render.com (configured via Procfile)
- **Process**: `web: python app.py`
- **Environment**: Production settings auto-detected
- **File Storage**: Local filesystem (ephemeral on Render)