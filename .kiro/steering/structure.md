# Project Structure & Organization

## Root Directory Layout
```
SoundCloud_Downloader/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── Procfile                 # Render.com deployment config
├── README.md                # Main project documentation
├── .gitignore              # Git ignore patterns
├── LICENSE                 # Project license
├── templates/              # Jinja2 HTML templates
├── descargas/              # Download directory (auto-created)
└── .kiro/                  # Kiro IDE configuration
```

## Template Structure
```
templates/
├── base.html               # Base template with navbar, footer, theme system
├── index.html              # Main download page
├── downloads.html          # File management page
└── install.html            # System configuration page
```

## Key File Responsibilities

### `app.py` - Main Application
- Flask route definitions and request handling
- Download logic using yt-dlp
- File management and ZIP compression
- Progress tracking and status endpoints
- Global variables for download state management

### `templates/base.html` - Base Template
- Complete CSS framework with custom variables
- Dark/light theme system with toggle
- Responsive navbar and footer
- AdSense integration placeholders
- Bootstrap and Font Awesome CDN imports

### `templates/index.html` - Download Interface
- URL input with auto-detection
- Download type selection (single/playlist)
- Progress tracking with real-time updates
- Auto-download toggle and timing options
- JavaScript for form handling and AJAX requests

### `templates/downloads.html` - File Management
- File listing with metadata (size, date, type)
- Download statistics and counters
- Individual file download buttons
- Auto-download functionality for individual files

## Naming Conventions

### Python Code
- **Functions**: `snake_case` (e.g., `descargar_contenido_async`)
- **Variables**: `snake_case` (e.g., `download_status`, `current_track`)
- **Constants**: `UPPER_SNAKE_CASE` for configuration values
- **Classes**: `PascalCase` (if any are added)

### Frontend Code
- **CSS Classes**: `kebab-case` with BEM-like modifiers (e.g., `card-glass`, `btn-gradient`)
- **JavaScript Functions**: `camelCase` (e.g., `monitorProgress`, `updateProgressUI`)
- **HTML IDs**: `camelCase` (e.g., `downloadForm`, `progressArea`)

### File Organization
- **Downloads**: Saved to `descargas/` with original titles
- **Playlists**: Organized in subfolders or compressed to ZIP
- **Templates**: Semantic names reflecting their purpose
- **Documentation**: Descriptive markdown files in root

## State Management

### Global Variables (app.py)
- `download_status`: Track download state by ID
- `download_progress`: Store progress information
- `download_results`: Cache file paths for completed downloads

### Frontend State (JavaScript)
- `currentDownloadId`: Active download identifier
- `progressInterval`: Timer for status polling
- `downloadedFiles`: Array of completed file paths
- `isPlaylist`: Boolean flag for playlist handling

## URL Structure
- `/` - Main download interface
- `/download` - POST endpoint for initiating downloads
- `/status/<download_id>` - GET progress information
- `/downloads` - File management page
- `/download_file/<filename>` - Direct file download
- `/auto_download/<download_id>` - Automatic download trigger