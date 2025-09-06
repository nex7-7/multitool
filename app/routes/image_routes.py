"""
Image processing API routes.
Handles all image-related HTTP requests following RESTful principles.
"""

from flask import Blueprint, request, jsonify, Response, current_app, url_for
from werkzeug.utils import secure_filename
from typing import Dict, Any, Optional, Tuple, Union
import os
import tempfile
import uuid
from pathlib import Path

from ..tools.image.processors import (
    ImageResizer, ImageCropper, ImageRotator, 
    ImageEnhancer, BackgroundRemover, FormatConverter
)
from ..utils.base import FileValidator
from ..config import Config

image_bp = Blueprint('image', __name__)

def _validate_image_file(file) -> Optional[str]:
    """
    Validate uploaded image file.
    
    Args:
        file: Uploaded file object
        
    Returns:
        Optional[str]: Error message if validation fails, None if valid
    """
    if not file or not file.filename:
        return "No file provided"
    
    if not FileValidator.is_allowed_extension(file.filename, Config.ALLOWED_IMAGE_EXTENSIONS):
        return f"Invalid file type. Allowed: {', '.join(Config.ALLOWED_IMAGE_EXTENSIONS)}"
    
    return None

def _save_uploaded_file(file, prefix: str = "upload") -> str:
    """
    Save uploaded file to temporary location.
    
    Args:
        file: Uploaded file object
        prefix: Filename prefix
        
    Returns:
        str: Path to saved file
    """
    filename = secure_filename(file.filename)
    safe_filename = FileValidator.get_safe_filename(f"{prefix}_{uuid.uuid4()}_{filename}")
    filepath = current_app.config['UPLOAD_FOLDER'] / safe_filename
    file.save(filepath)
    return str(filepath)

def _generate_output_path(input_path: str, suffix: str = "processed") -> str:
    """
    Generate output file path.
    
    Args:
        input_path: Input file path
        suffix: Suffix to add to filename
        
    Returns:
        str: Output file path
    """
    input_file = Path(input_path)
    output_filename = f"{input_file.stem}_{suffix}_{uuid.uuid4()}{input_file.suffix}"
    return str(current_app.config['OUTPUT_FOLDER'] / output_filename)

@image_bp.route('/resize', methods=['POST'])
def resize_image() -> Union[Tuple[Response, int], Response]:
    """
    Resize an uploaded image.
    
    Expected form data:
        - file: Image file
        - width: Target width (int)
        - height: Target height (int)
        - maintain_aspect: Whether to maintain aspect ratio (bool, optional)
        
    Returns:
        Response: JSON response with operation result
    """
    try:
        # Validate file
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        error = _validate_image_file(file)
        if error:
            return jsonify({'error': error}), 400
        
        # Get parameters
        try:
            width = int(request.form.get('width', 0))
            height = int(request.form.get('height', 0))
        except ValueError:
            return jsonify({'error': 'Invalid width or height values'}), 400
        
        if width <= 0 or height <= 0:
            return jsonify({'error': 'Width and height must be positive integers'}), 400
        
        maintain_aspect = request.form.get('maintain_aspect', 'true').lower() == 'true'
        
        # Save uploaded file
        input_path = _save_uploaded_file(file, "resize_input")
        output_path = _generate_output_path(input_path, "resized")
        
        # Process image
        resizer = ImageResizer(input_path, output_path)
        result = resizer.process(width=width, height=height, maintain_aspect=maintain_aspect)
        
        # Cleanup input file
        os.remove(input_path)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@image_bp.route('/crop', methods=['POST'])
def crop_image() -> Union[Tuple[Response, int], Response]:
    """
    Crop an uploaded image.
    
    Expected form data:
        - file: Image file
        - x: Left coordinate (int)
        - y: Top coordinate (int)
        - width: Crop width (int)
        - height: Crop height (int)
        
    Returns:
        Response: JSON response with operation result
    """
    try:
        # Validate file
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        error = _validate_image_file(file)
        if error:
            return jsonify({'error': error}), 400
        
        # Get parameters
        try:
            x = int(request.form.get('x', 0))
            y = int(request.form.get('y', 0))
            width = int(request.form.get('width', 0))
            height = int(request.form.get('height', 0))
        except ValueError:
            return jsonify({'error': 'Invalid coordinate or dimension values'}), 400
        
        if x < 0 or y < 0 or width <= 0 or height <= 0:
            return jsonify({'error': 'Invalid crop coordinates or dimensions'}), 400
        
        # Save uploaded file
        input_path = _save_uploaded_file(file, "crop_input")
        output_path = _generate_output_path(input_path, "cropped")
        
        # Process image
        cropper = ImageCropper(input_path, output_path)
        result = cropper.process(x=x, y=y, width=width, height=height)
        
        # Cleanup input file
        os.remove(input_path)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@image_bp.route('/rotate', methods=['POST'])
def rotate_image() -> Union[Tuple[Response, int], Response]:
    """
    Rotate an uploaded image.
    
    Expected form data:
        - file: Image file
        - angle: Rotation angle in degrees (float)
        - expand: Whether to expand image to fit (bool, optional)
        
    Returns:
        Response: JSON response with operation result
    """
    try:
        # Validate file
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        error = _validate_image_file(file)
        if error:
            return jsonify({'error': error}), 400
        
        # Get parameters
        try:
            angle = float(request.form.get('angle', 0))
        except ValueError:
            return jsonify({'error': 'Invalid angle value'}), 400
        
        expand = request.form.get('expand', 'true').lower() == 'true'
        
        # Save uploaded file
        input_path = _save_uploaded_file(file, "rotate_input")
        output_path = _generate_output_path(input_path, "rotated")
        
        # Process image
        rotator = ImageRotator(input_path, output_path)
        result = rotator.process(angle=angle, expand=expand)
        
        # Cleanup input file
        os.remove(input_path)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@image_bp.route('/enhance', methods=['POST'])
def enhance_image() -> Union[Tuple[Response, int], Response]:
    """
    Enhance an uploaded image (brightness, contrast, etc.).
    
    Expected form data:
        - file: Image file
        - brightness: Brightness factor (float, optional, default 1.0)
        - contrast: Contrast factor (float, optional, default 1.0)
        - saturation: Saturation factor (float, optional, default 1.0)
        - sharpness: Sharpness factor (float, optional, default 1.0)
        
    Returns:
        Response: JSON response with operation result
    """
    try:
        # Validate file
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        error = _validate_image_file(file)
        if error:
            return jsonify({'error': error}), 400
        
        # Get parameters
        try:
            brightness = float(request.form.get('brightness', 1.0))
            contrast = float(request.form.get('contrast', 1.0))
            saturation = float(request.form.get('saturation', 1.0))
            sharpness = float(request.form.get('sharpness', 1.0))
        except ValueError:
            return jsonify({'error': 'Invalid enhancement parameter values'}), 400
        
        # Validate parameter ranges
        for value, name in [(brightness, 'brightness'), (contrast, 'contrast'), 
                           (saturation, 'saturation'), (sharpness, 'sharpness')]:
            if not 0.1 <= value <= 3.0:
                return jsonify({'error': f'{name} must be between 0.1 and 3.0'}), 400
        
        # Save uploaded file
        input_path = _save_uploaded_file(file, "enhance_input")
        output_path = _generate_output_path(input_path, "enhanced")
        
        # Process image
        enhancer = ImageEnhancer(input_path, output_path)
        result = enhancer.process(
            brightness=brightness, 
            contrast=contrast, 
            saturation=saturation, 
            sharpness=sharpness
        )
        
        # Cleanup input file
        os.remove(input_path)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@image_bp.route('/remove-background', methods=['POST'])
@image_bp.route('/remove-bg', methods=['POST'])
def remove_background() -> Union[Tuple[Response, int], Response]:
    """
    Remove background from an uploaded image using YOLO segmentation.
    
    Expected form data:
        - file: Image file
        - foreground_points: JSON string of foreground points (optional)
        
    Returns:
        Response: JSON response with operation result
    """
    try:
        import json
        
        # Validate file
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        error = _validate_image_file(file)
        if error:
            return jsonify({'error': error}), 400
        
        # Get foreground points if provided
        foreground_points = None
        if 'foreground_points' in request.form:
            try:
                points_str = request.form.get('foreground_points')
                foreground_points = json.loads(points_str) if points_str else None
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid foreground_points JSON'}), 400
        
        # Save uploaded file
        input_path = _save_uploaded_file(file, "bg_remove_input")
        output_path = _generate_output_path(input_path, "no_bg")
        # Change extension to PNG for transparency support
        output_path = str(Path(output_path).with_suffix('.png'))
        
        # Process image
        bg_remover = BackgroundRemover(input_path, output_path)
        result = bg_remover.process(foreground_points=foreground_points)
        
        # Cleanup input file
        os.remove(input_path)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@image_bp.route('/convert-format', methods=['POST'])
@image_bp.route('/convert', methods=['POST'])
def convert_format() -> Union[Tuple[Response, int], Response]:
    """
    Convert image to different format.
    
    Expected form data:
        - file: Image file
        - target_format: Target format (e.g., 'JPEG', 'PNG', 'WEBP')
        - quality: Quality for lossy formats (int, optional, default 95)
        
    Returns:
        Response: JSON response with operation result
    """
    try:
        # Validate file
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        error = _validate_image_file(file)
        if error:
            return jsonify({'error': error}), 400
        
        # Get parameters
        target_format = request.form.get('target_format', '').upper()
        if not target_format:
            return jsonify({'error': 'Target format is required'}), 400
        
        allowed_formats = {'JPEG', 'PNG', 'WEBP', 'BMP', 'TIFF'}
        if target_format not in allowed_formats:
            return jsonify({'error': f'Unsupported format. Allowed: {", ".join(allowed_formats)}'}), 400
        
        try:
            quality = int(request.form.get('quality', 95))
        except ValueError:
            return jsonify({'error': 'Invalid quality value'}), 400
        
        if not 1 <= quality <= 100:
            return jsonify({'error': 'Quality must be between 1 and 100'}), 400
        
        # Save uploaded file
        input_path = _save_uploaded_file(file, "convert_input")
        output_path = _generate_output_path(input_path, "converted")
        # Update extension based on target format
        format_extensions = {
            'JPEG': '.jpg',
            'PNG': '.png', 
            'WEBP': '.webp',
            'BMP': '.bmp',
            'TIFF': '.tiff'
        }
        output_path = str(Path(output_path).with_suffix(format_extensions[target_format]))
        
        # Process image
        converter = FormatConverter(input_path, output_path)
        result = converter.process(target_format=target_format, quality=quality)
        
        # Cleanup input file
        os.remove(input_path)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@image_bp.route('/info/<filename>')
def get_image_info(filename: str) -> Union[Tuple[Response, int], Response]:
    """
    Get information about a processed image file.
    
    Args:
        filename: Name of the image file
        
    Returns:
        Response: JSON response with image information
    """
    try:
        filepath = current_app.config['OUTPUT_FOLDER'] / secure_filename(filename)
        
        if not filepath.exists():
            return jsonify({'error': 'File not found'}), 404
        
        # Use a dummy tool instance to get file info
        from ..tools.image.processors import ImageResizer
        tool = ImageResizer(str(filepath))
        info = tool.get_file_info()
        
        return jsonify(info), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get file info: {str(e)}'}), 500
