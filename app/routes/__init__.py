"""
Route registration and URL handling.
Follows Open/Closed Principle - easy to add new routes without modifying existing code.
"""

from flask import Flask
from .main_routes import main_bp
from .image_routes import image_bp
from .video_routes import video_bp
from .pdf_routes import pdf_bp

def register_routes(app: Flask) -> None:
    """
    Register all application blueprints.
    
    Args:
        app: Flask application instance
    """
    # Main application routes
    app.register_blueprint(main_bp)
    
    # Tool-specific routes
    app.register_blueprint(image_bp, url_prefix='/api/image')
    app.register_blueprint(video_bp, url_prefix='/api/video')
    app.register_blueprint(pdf_bp, url_prefix='/api/pdf')
