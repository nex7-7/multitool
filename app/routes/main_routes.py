"""
Main application routes for the MultiTool interface.
Handles the primary UI and navigation.
"""

from flask import Blueprint, render_template, jsonify, Response, send_from_directory, current_app
from typing import Union
from pathlib import Path

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index() -> str:
    """
    Render the main application interface.
    
    Returns:
        str: Rendered HTML template
    """
    return render_template('index.html')

@main_bp.route('/api/health')
def health_check() -> Response:
    """
    Simple health check endpoint.
    
    Returns:
        Response: JSON response with health status
    """
    return jsonify({
        'status': 'healthy',
        'message': 'MultiTool API is running'
    })

@main_bp.route('/output/<path:filename>')
def serve_output_file(filename) -> Response:
    """
    Serve processed output files.
    
    Args:
        filename: Name of the output file
        
    Returns:
        Response: File response for download
    """
    return send_from_directory(current_app.config['OUTPUT_FOLDER'], filename, as_attachment=False)
