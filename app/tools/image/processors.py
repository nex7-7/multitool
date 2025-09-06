"""
Image processing tools implementation.
Each class follows Single Responsibility Principle - one tool, one responsibility.
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from typing import Dict, Any, Tuple, Optional, List
from pathlib import Path
import logging
from flask import url_for
from ultralytics import YOLO

from ...utils.base import ToolBase, ProcessingResult

logger = logging.getLogger(__name__)

def _build_output_url(output_path: Path) -> str:
    """Return the public URL for a saved output file.

    Uses only the filename to avoid leaking absolute paths and to work cross-platform.
    """
    return url_for('main.serve_output_file', filename=Path(output_path).name, _external=True)

def _to_numpy(x) -> np.ndarray:
    """Convert various tensor/array types to numpy ndarray safely."""
    cpu = getattr(x, 'cpu', None)
    if callable(cpu):
        x = cpu()
    to_numpy = getattr(x, 'numpy', None)
    if callable(to_numpy):
        x = to_numpy()
    return np.asarray(x)

class ImageResizer(ToolBase):
    """Handles image resizing operations."""
    
    def process(self, width: int, height: int, maintain_aspect: bool = True, **kwargs) -> Dict[str, Any]:
        """
        Resize image to specified dimensions.
        
        Args:
            width: Target width in pixels
            height: Target height in pixels
            maintain_aspect: Whether to maintain aspect ratio
            
        Returns:
            Dict[str, Any]: Processing result
        """
        try:
            with Image.open(self.input_path) as img:
                if maintain_aspect:
                    img.thumbnail((width, height), Image.Resampling.LANCZOS)
                else:
                    img = img.resize((width, height), Image.Resampling.LANCZOS)
                
                if self.output_path:
                    img.save(self.output_path, optimize=True)
                    output_url = _build_output_url(Path(self.output_path))
                    result = ProcessingResult(
                        success=True,
                        message=f"Image resized to {img.size[0]}x{img.size[1]}",
                        output_path=str(self.output_path),
                        output_url=output_url,
                        metadata={'new_size': img.size, 'original_size': Image.open(self.input_path).size}
                    )
                else:
                    result = ProcessingResult(
                        success=True,
                        message="Image resized in memory",
                        metadata={'new_size': img.size}
                    )
                
                return result.to_dict()
                
        except Exception as e:
            logger.error(f"Error resizing image: {str(e)}")
            return ProcessingResult(False, f"Failed to resize image: {str(e)}").to_dict()

class ImageCropper(ToolBase):
    """Handles image cropping operations."""
    
    def process(self, x: int, y: int, width: int, height: int, **kwargs) -> Dict[str, Any]:
        """
        Crop image to specified rectangle.
        
        Args:
            x: Left coordinate
            y: Top coordinate
            width: Crop width
            height: Crop height
            
        Returns:
            Dict[str, Any]: Processing result
        """
        try:
            with Image.open(self.input_path) as img:
                # Validate crop coordinates
                img_width, img_height = img.size
                if x + width > img_width or y + height > img_height:
                    return ProcessingResult(
                        False, 
                        "Crop coordinates exceed image boundaries"
                    ).to_dict()
                
                cropped = img.crop((x, y, x + width, y + height))
                
                if self.output_path:
                    cropped.save(self.output_path, optimize=True)
                    result = ProcessingResult(
                        success=True,
                        message=f"Image cropped to {width}x{height}",
                        output_path=str(self.output_path),
                        output_url=_build_output_url(Path(self.output_path)),
                        metadata={
                            'crop_area': {'x': x, 'y': y, 'width': width, 'height': height},
                            'original_size': img.size
                        }
                    )
                else:
                    result = ProcessingResult(
                        success=True,
                        message="Image cropped in memory",
                        metadata={'crop_area': {'x': x, 'y': y, 'width': width, 'height': height}}
                    )
                
                return result.to_dict()
                
        except Exception as e:
            logger.error(f"Error cropping image: {str(e)}")
            return ProcessingResult(False, f"Failed to crop image: {str(e)}").to_dict()

class ImageRotator(ToolBase):
    """Handles image rotation operations."""
    
    def process(self, angle: float, expand: bool = True, **kwargs) -> Dict[str, Any]:
        """
        Rotate image by specified angle.
        
        Args:
            angle: Rotation angle in degrees (positive = clockwise)
            expand: Whether to expand image to fit rotated content
            
        Returns:
            Dict[str, Any]: Processing result
        """
        try:
            with Image.open(self.input_path) as img:
                # Rotate image
                rotated = img.rotate(-angle, expand=expand, fillcolor='white')
                
                if self.output_path:
                    rotated.save(self.output_path, optimize=True)
                    result = ProcessingResult(
                        success=True,
                        message=f"Image rotated by {angle} degrees",
                        output_path=str(self.output_path),
                        output_url=_build_output_url(Path(self.output_path)),
                        metadata={
                            'rotation_angle': angle,
                            'expanded': expand,
                            'original_size': img.size,
                            'new_size': rotated.size
                        }
                    )
                else:
                    result = ProcessingResult(
                        success=True,
                        message="Image rotated in memory",
                        metadata={'rotation_angle': angle, 'new_size': rotated.size}
                    )
                
                return result.to_dict()
                
        except Exception as e:
            logger.error(f"Error rotating image: {str(e)}")
            return ProcessingResult(False, f"Failed to rotate image: {str(e)}").to_dict()

class ImageEnhancer(ToolBase):
    """Handles image enhancement operations (brightness, contrast, etc.)."""
    
    def process(self, brightness: float = 1.0, contrast: float = 1.0, 
                saturation: float = 1.0, sharpness: float = 1.0, **kwargs) -> Dict[str, Any]:
        """
        Enhance image with various adjustments.
        
        Args:
            brightness: Brightness factor (1.0 = no change, >1.0 = brighter)
            contrast: Contrast factor (1.0 = no change, >1.0 = more contrast)
            saturation: Saturation factor (1.0 = no change, >1.0 = more saturated)
            sharpness: Sharpness factor (1.0 = no change, >1.0 = sharper)
            
        Returns:
            Dict[str, Any]: Processing result
        """
        try:
            with Image.open(self.input_path) as img:
                # Apply enhancements
                if brightness != 1.0:
                    enhancer = ImageEnhance.Brightness(img)
                    img = enhancer.enhance(brightness)
                
                if contrast != 1.0:
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(contrast)
                
                if saturation != 1.0:
                    enhancer = ImageEnhance.Color(img)
                    img = enhancer.enhance(saturation)
                
                if sharpness != 1.0:
                    enhancer = ImageEnhance.Sharpness(img)
                    img = enhancer.enhance(sharpness)
                
                if self.output_path:
                    img.save(self.output_path, optimize=True)
                    result = ProcessingResult(
                        success=True,
                        message="Image enhanced successfully",
                        output_path=str(self.output_path),
                        output_url=_build_output_url(Path(self.output_path)),
                        metadata={
                            'adjustments': {
                                'brightness': brightness,
                                'contrast': contrast,
                                'saturation': saturation,
                                'sharpness': sharpness
                            }
                        }
                    )
                else:
                    result = ProcessingResult(
                        success=True,
                        message="Image enhanced in memory",
                        metadata={'adjustments': {'brightness': brightness, 'contrast': contrast}}
                    )
                
                return result.to_dict()
                
        except Exception as e:
            logger.error(f"Error enhancing image: {str(e)}")
            return ProcessingResult(False, f"Failed to enhance image: {str(e)}").to_dict()

class BackgroundRemover(ToolBase):
    """Handles background removal using YOLO segmentation."""
    
    def __init__(self, input_path: str, output_path: Optional[str] = None, model_name: str = 'yolo11n-seg.pt'):
        """
        Initialize background remover with YOLO model.
        
        Args:
            input_path: Path to input image
            output_path: Path to output image
            model_name: YOLO model name to use
        """
        super().__init__(input_path, output_path)
        self.model_name = model_name
        self._model = None
    
    def _load_model(self) -> YOLO:
        """Load YOLO model lazily for better performance."""
        if self._model is None:
            self._model = YOLO(self.model_name)
        return self._model
    
    def process(self, foreground_points: Optional[List[Tuple[int, int]]] = None, **kwargs) -> Dict[str, Any]:
        """
        Remove background from image using segmentation.
        
        Args:
            foreground_points: List of (x, y) points indicating foreground objects
            
        Returns:
            Dict[str, Any]: Processing result
        """
        try:
            model = self._load_model()
            
            # Load image
            img = cv2.imread(str(self.input_path))
            if img is None:
                return ProcessingResult(False, "Could not load image").to_dict()
            
            # Run segmentation
            results = model(img)

            if not results or not hasattr(results[0], 'masks') or results[0].masks is None:
                return ProcessingResult(False, "No objects detected for segmentation").to_dict()

            # Create mask from segmentation results (resize to original image size)
            masks_data = results[0].masks.data  # (n, mh, mw) tensor
            masks_array = _to_numpy(masks_data)
            orig_h, orig_w = img.shape[:2]

            resized_masks: List[np.ndarray] = []
            for m in masks_array:
                # Binarize and resize mask to original resolution
                m_bin = (m > 0.5).astype(np.uint8)
                m_resized = cv2.resize(m_bin, (orig_w, orig_h), interpolation=cv2.INTER_NEAREST).astype(bool)
                resized_masks.append(m_resized)

            if not resized_masks:
                return ProcessingResult(False, "No valid masks produced by the model").to_dict()

            resized_masks_arr = np.stack(resized_masks, axis=0)

            # Combine masks (optionally guided by points)
            if foreground_points:
                combined_mask = self._create_mask_from_points(resized_masks_arr, foreground_points, (orig_h, orig_w))
            else:
                combined_mask = np.any(resized_masks_arr, axis=0)

            # Apply mask to create transparent background
            img_rgba = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
            img_rgba[:, :, 3] = (combined_mask.astype(np.uint8) * 255)
            
            if self.output_path:
                cv2.imwrite(str(self.output_path), img_rgba)
                result = ProcessingResult(
                    success=True,
                    message="Background removed successfully",
                    output_path=str(self.output_path),
                    output_url=_build_output_url(Path(self.output_path)),
                    metadata={
                        'segments_detected': int(resized_masks_arr.shape[0]),
                        'foreground_points_used': bool(foreground_points)
                    }
                )
            else:
                result = ProcessingResult(
                    success=True,
                    message="Background removed in memory",
                    metadata={'segments_detected': int(resized_masks_arr.shape[0])}
                )
            
            return result.to_dict()
            
        except Exception as e:
            logger.error(f"Error removing background: {str(e)}")
            return ProcessingResult(False, f"Failed to remove background: {str(e)}").to_dict()
    
    def _create_mask_from_points(self, masks: np.ndarray, points: List[Tuple[int, int]], 
                                img_shape: Tuple[int, int]) -> np.ndarray:
        """
        Create combined mask based on user-selected points.
        
        Args:
            masks: Segmentation masks from YOLO
            points: User-selected foreground points
            img_shape: Image dimensions (height, width)
            
        Returns:
            np.ndarray: Combined binary mask
        """
        combined_mask = np.zeros(img_shape, dtype=bool)

        for mask in masks:
            # Check if any user point falls within this mask
            for x, y in points:
                if 0 <= y < mask.shape[0] and 0 <= x < mask.shape[1] and mask[y, x]:
                    combined_mask |= mask
                    break

        return combined_mask

class FormatConverter(ToolBase):
    """Handles image format conversion."""
    
    def process(self, target_format: str, quality: int = 95, **kwargs) -> Dict[str, Any]:
        """
        Convert image to different format.
        
        Args:
            target_format: Target format (e.g., 'JPEG', 'PNG', 'WEBP')
            quality: Quality for lossy formats (1-100)
            
        Returns:
            Dict[str, Any]: Processing result
        """
        try:
            with Image.open(self.input_path) as img:
                # Handle transparency for formats that don't support it
                if target_format.upper() == 'JPEG' and img.mode in ('RGBA', 'LA'):
                    # Create white background for JPEG
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                if self.output_path:
                    save_kwargs = {'format': target_format.upper(), 'optimize': True}
                    if target_format.upper() in ('JPEG', 'WEBP'):
                        save_kwargs['quality'] = quality
                    
                    img.save(self.output_path, **save_kwargs)
                    
                    result = ProcessingResult(
                        success=True,
                        message=f"Image converted to {target_format.upper()}",
                        output_path=str(self.output_path),
                        output_url=_build_output_url(Path(self.output_path)),
                        metadata={
                            'original_format': self.input_path.suffix.upper().lstrip('.'),
                            'target_format': target_format.upper(),
                            'quality': quality if target_format.upper() in ('JPEG', 'WEBP') else None
                        }
                    )
                else:
                    result = ProcessingResult(
                        success=True,
                        message=f"Image converted to {target_format.upper()} in memory",
                        metadata={'target_format': target_format.upper()}
                    )
                
                return result.to_dict()
                
        except Exception as e:
            logger.error(f"Error converting image format: {str(e)}")
            return ProcessingResult(False, f"Failed to convert image format: {str(e)}").to_dict()
