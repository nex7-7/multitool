"""
Configuration settings for the MultiTool application.
Centralizes all configuration in one place following DRY principle.
"""

import os
from pathlib import Path

class Config:
    """Application configuration class."""
    
    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = True
    
    # File handling settings
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size
    UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
    OUTPUT_FOLDER = Path(__file__).parent / 'output'
    
    # Allowed file extensions
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'}
    ALLOWED_PDF_EXTENSIONS = {'pdf'}
    
    # Tool-specific settings
    YOLO_MODEL_NAME = 'yolo11n-seg.pt'  # For background removal
    FFMPEG_TIMEOUT = 300  # 5 minutes timeout for video operations
