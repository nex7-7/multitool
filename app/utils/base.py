"""
Base classes and interfaces for tool operations.
Follows Interface Segregation Principle and provides common functionality.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pathlib import Path
import os

class ToolBase(ABC):
    """
    Abstract base class for all tool operations.
    Enforces consistent interface across all tools (Interface Segregation Principle).
    """
    
    def __init__(self, input_path: str, output_path: Optional[str] = None):
        """
        Initialize tool with input and output paths.
        
        Args:
            input_path: Path to input file
            output_path: Path to output file (optional)
        """
        self.input_path = Path(input_path)
        self.output_path = Path(output_path) if output_path else None
        self._validate_input_file()
    
    def _validate_input_file(self) -> None:
        """
        Validate that input file exists and is readable.
        
        Raises:
            FileNotFoundError: If input file doesn't exist
            PermissionError: If input file is not readable
        """
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_path}")
        
        if not os.access(self.input_path, os.R_OK):
            raise PermissionError(f"Cannot read input file: {self.input_path}")
    
    @abstractmethod
    def process(self, **kwargs) -> Dict[str, Any]:
        """
        Process the input file according to tool-specific logic.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            Dict[str, Any]: Processing result with status and output information
        """
        pass
    
    def get_file_info(self) -> Dict[str, Any]:
        """
        Get basic information about the input file.
        
        Returns:
            Dict[str, Any]: File information including size, extension, etc.
        """
        stat = self.input_path.stat()
        return {
            'filename': self.input_path.name,
            'size': stat.st_size,
            'extension': self.input_path.suffix.lower(),
            'created': stat.st_ctime,
            'modified': stat.st_mtime
        }

class FileValidator:
    """
    Utility class for file validation operations.
    Follows Single Responsibility Principle - only handles file validation.
    """
    
    @staticmethod
    def is_allowed_extension(filename: str, allowed_extensions: set) -> bool:
        """
        Check if file has an allowed extension.
        
        Args:
            filename: Name of the file to check
            allowed_extensions: Set of allowed file extensions
            
        Returns:
            bool: True if extension is allowed, False otherwise
        """
        extension = Path(filename).suffix.lower().lstrip('.')
        return extension in allowed_extensions
    
    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """
        Generate a safe filename by removing/replacing unsafe characters.
        
        Args:
            filename: Original filename
            
        Returns:
            str: Safe filename for file system operations
        """
        import re
        # Remove unsafe characters and normalize
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove multiple underscores
        safe_name = re.sub(r'_+', '_', safe_name)
        return safe_name.strip('_')

class ProcessingResult:
    """
    Standardized result object for all tool operations.
    Provides consistent interface for operation results.
    """
    
    def __init__(self, success: bool, message: str, output_path: Optional[str] = None, 
                 output_url: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize processing result.
        
        Args:
            success: Whether operation was successful
            message: Human-readable message about the operation
            output_path: Path to output file if applicable
            output_url: URL to access the output file
            metadata: Additional metadata about the operation
        """
        self.success = success
        self.message = message
        self.output_path = output_path
        self.output_url = output_url
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary for JSON serialization.
        
        Returns:
            Dict[str, Any]: Serializable result dictionary
        """
        return {
            'success': self.success,
            'message': self.message,
            'output_path': self.output_path,
            'output_url': self.output_url,
            'metadata': self.metadata
        }
