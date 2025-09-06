# MultiTool

A comprehensive all-in-one file processing application built with Flask and Python. Process images, videos, and PDFs with ease using our intuitive web interface.

## Features

### Image Tools ✅ (Implemented)
- **Resize Image**: Change dimensions while maintaining quality
- **Crop Image**: Extract specific regions from images
- **Rotate Image**: Rotate images by any angle with precision
- **Enhance Image**: Adjust brightness, contrast, saturation, and sharpness
- **Remove Background**: AI-powered background removal using YOLO segmentation
- **Convert Format**: Convert between JPEG, PNG, WebP, BMP, and TIFF formats

### Video Tools 🚧 (Coming Soon)
- **Download Video**: Download videos from various web platforms
- **Extract Audio**: Extract audio tracks from video files
- **Trim Video**: Cut and trim videos to specific time ranges  
- **Convert Format**: Convert between MP4, AVI, MOV, and other formats

### PDF Tools 🚧 (Coming Soon)
- **Split PDF**: Split PDF into separate pages or sections
- **Merge PDFs**: Combine multiple PDF files into one document
- **Rearrange Pages**: Reorder pages within a PDF document
- **Convert to PDF**: Convert documents and images to PDF format
- **Extract Text**: Extract text content from PDF documents

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd multitool
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Ensure FFmpeg is installed** (for video processing)
   - Windows: Download from https://ffmpeg.org/download.html
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

## Usage

1. **Start the application**
   ```bash
   python app.py
   ```

2. **Open your browser**
   Navigate to `http://127.0.0.1:5000`

3. **Use the tools**
   - Select a tool category (Image, Video, PDF)
   - Click on a specific tool
   - Upload your file and configure settings
   - Process and download the result

## API Endpoints

### Image Processing
- `POST /api/image/resize` - Resize images
- `POST /api/image/crop` - Crop images  
- `POST /api/image/rotate` - Rotate images
- `POST /api/image/enhance` - Enhance image properties
- `POST /api/image/remove-background` - Remove backgrounds
- `POST /api/image/convert-format` - Convert image formats

### Video Processing (Coming Soon)
- `POST /api/video/download` - Download videos
- `POST /api/video/extract-audio` - Extract audio
- `POST /api/video/trim` - Trim videos
- `POST /api/video/convert-format` - Convert video formats

### PDF Processing (Coming Soon)  
- `POST /api/pdf/split` - Split PDFs
- `POST /api/pdf/merge` - Merge PDFs
- `POST /api/pdf/rearrange` - Rearrange pages
- `POST /api/pdf/convert-to-pdf` - Convert to PDF
- `POST /api/pdf/extract-text` - Extract text

## Architecture

The application follows Clean Code principles and SOLID design patterns:

### Directory Structure
```
multitool/
├── app/
│   ├── routes/          # API route handlers
│   ├── tools/           # Tool implementations
│   │   ├── image/       # Image processing tools
│   │   ├── video/       # Video processing tools (coming soon)
│   │   └── pdf/         # PDF processing tools (coming soon)
│   ├── utils/           # Shared utilities and base classes
│   ├── static/          # CSS, JavaScript, and static assets
│   ├── templates/       # HTML templates
│   ├── uploads/         # Temporary upload storage
│   ├── output/          # Processed file output
│   └── config.py        # Application configuration
├── app.py               # Application entry point
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Design Principles
- **Single Responsibility Principle**: Each tool class handles one specific operation
- **Open/Closed Principle**: Easy to add new tools without modifying existing code
- **Interface Segregation**: Clean separation between tool types and operations
- **Dependency Inversion**: Abstract base classes define consistent interfaces
- **DRY (Don't Repeat Yourself)**: Shared utilities prevent code duplication

## Technology Stack

- **Backend**: Python 3.11+ with Flask
- **Frontend**: Vanilla JavaScript with modern CSS
- **Image Processing**: OpenCV, Pillow, Ultralytics YOLO
- **Video Processing**: yt-dlp, FFmpeg, MoviePy
- **PDF Processing**: PyMuPDF, pdfplumber, pypdf
- **UI/UX**: Font Awesome icons, responsive design

## Configuration

Key configuration options in `app/config.py`:

- `MAX_CONTENT_LENGTH`: Maximum file upload size (500MB default)
- `ALLOWED_IMAGE_EXTENSIONS`: Supported image formats
- `ALLOWED_VIDEO_EXTENSIONS`: Supported video formats  
- `ALLOWED_PDF_EXTENSIONS`: Supported PDF formats
- `YOLO_MODEL_NAME`: YOLO model for background removal

## Development

### Adding New Tools

1. **Create tool class** in appropriate `tools/` subdirectory
2. **Inherit from `ToolBase`** and implement `process()` method
3. **Add route handler** in corresponding `routes/` file
4. **Update frontend** with tool UI and integration

### Code Style
- Follow PEP 8 guidelines
- Use type hints for better code documentation
- Write docstrings for all classes and methods
- Implement proper error handling and logging

## Security Considerations

- File type validation on upload
- Safe filename generation
- Input parameter validation
- Error message sanitization
- Temporary file cleanup

## Performance

- Lazy loading of ML models (YOLO)
- Asynchronous file processing
- Efficient memory management
- Optimized image operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow coding standards
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **OpenCV** for computer vision operations
- **Ultralytics** for YOLO segmentation models
- **FFmpeg** for video processing capabilities
- **Flask** for the web framework foundation
