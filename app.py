"""
Main Flask application entry point.
Follows Single Responsibility Principle - only handles app initialization and routing setup.
"""

from flask import Flask
from flask_cors import CORS
from app.routes import register_routes
from app.config import Config
import os

def create_app() -> Flask:
    """
    Application factory pattern for better testability and configuration management.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
    app.config.from_object(Config)
    
    # Enable CORS for frontend-backend communication
    CORS(app)
    
    # Ensure required directories exist
    _ensure_directories_exist(app)
    
    # Register all routes
    register_routes(app)
    
    return app

def _ensure_directories_exist(app: Flask) -> None:
    """
    Ensure all required directories exist for file operations.
    
    Args:
        app: Flask application instance
    """
    required_dirs = [
        app.config['UPLOAD_FOLDER'],
        app.config['OUTPUT_FOLDER']
    ]
    
    for directory in required_dirs:
        os.makedirs(directory, exist_ok=True)

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000)
